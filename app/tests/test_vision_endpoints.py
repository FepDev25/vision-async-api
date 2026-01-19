import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import Mock, patch, AsyncMock
from uuid import uuid4
from datetime import datetime, timezone
from app.main import app
from app.models import Task, TaskStatus
from io import BytesIO


@pytest.fixture
def mock_task():
    # Fixture que retorna una tarea mock
    task_id = uuid4()
    return Task(
        id=task_id,
        status=TaskStatus.PENDING,
        filename="test_image.jpg",
        result=None,
        created_at=datetime.now(timezone.utc),
        updated_at=None
    )


@pytest.fixture
def completed_task():
    # Fixture que retorna una tarea completada
    task_id = uuid4()
    return Task(
        id=task_id,
        status=TaskStatus.COMPLETED,
        filename="test_image.jpg",
        result={"processed_file": "processed_test_image.png"},
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


class TestAnalyzeEndpoint:
    # Tests para el endpoint POST /analyze
    
    @pytest.mark.asyncio
    @patch('app.routers.vision.MinioService')
    @patch('app.routers.vision.process_image')
    async def test_analyze_image_success(self, mock_process_image, mock_minio_service):
        # Test: Subir imagen exitosamente
        # Arrange
        mock_minio_instance = Mock()
        mock_minio_instance.upload_file.return_value = "stored_filename.jpg"
        mock_minio_service.return_value = mock_minio_instance
        
        mock_process_image.delay = Mock()
        
        # Crear imagen de prueba
        image_content = b"fake image content"
        files = {"file": ("test.jpg", BytesIO(image_content), "image/jpeg")}
        
        # Act
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/vision/analyze",
                files=files
            )
        
        # Assert
        assert response.status_code == 202
        data = response.json()
        assert "id" in data
        assert data["status"] == "PENDING"
        assert data["filename"] == "stored_filename.jpg"
        mock_minio_instance.upload_file.assert_called_once()
        mock_process_image.delay.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_analyze_invalid_file_type(self):
        # Test: Rechazar archivos que no sean imágenes
        # Arrange
        files = {"file": ("test.txt", BytesIO(b"not an image"), "text/plain")}
        
        # Act
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/vision/analyze",
                files=files
            )
        
        # Assert
        assert response.status_code == 400
        assert "imagen" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    @patch('app.routers.vision.MinioService')
    async def test_analyze_minio_error(self, mock_minio_service):
        # Test: Error al subir a MinIO
        # Arrange
        from app.services.storage import MinioServiceError
        mock_minio_instance = Mock()
        mock_minio_instance.upload_file.side_effect = MinioServiceError("Connection failed")
        mock_minio_service.return_value = mock_minio_instance
        
        files = {"file": ("test.jpg", BytesIO(b"image"), "image/jpeg")}
        
        # Act
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/vision/analyze",
                files=files
            )
        
        # Assert
        assert response.status_code == 500
        assert "almacenar" in response.json()["detail"].lower()


class TestGetTaskEndpoint:
    # Tests para el endpoint GET /tasks/{task_id}
    
    @pytest.mark.asyncio
    async def test_get_task_success(self, mock_task):
        # Test: Obtener tarea existente
        # Arrange
        from app.routers.vision import get_async_db
        
        async def override_get_db():
            mock_db = AsyncMock()
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = mock_task
            mock_db.execute.return_value = mock_result
            yield mock_db
        
        app.dependency_overrides[get_async_db] = override_get_db
        
        try:
            # Act
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    f"/api/v1/vision/tasks/{mock_task.id}"
                )
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == str(mock_task.id)
            assert data["status"] == mock_task.status.value
            assert data["filename"] == mock_task.filename
        finally:
            app.dependency_overrides.clear()
    
    @pytest.mark.asyncio
    async def test_get_task_not_found(self):
        # Test: Tarea no existe
        # Arrange
        from app.routers.vision import get_async_db
        
        async def override_get_db():
            mock_db = AsyncMock()
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = None
            mock_db.execute.return_value = mock_result
            yield mock_db
        
        app.dependency_overrides[get_async_db] = override_get_db
        
        fake_uuid = uuid4()
        
        try:
            # Act
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    f"/api/v1/vision/tasks/{fake_uuid}"
                )
            
            # Assert
            assert response.status_code == 404
            assert "no encontrada" in response.json()["detail"].lower()
        finally:
            app.dependency_overrides.clear()


class TestDownloadResultEndpoint:
    # Tests para el endpoint GET /tasks/{task_id}/result
    
    @pytest.mark.asyncio
    async def test_download_result_success(self, completed_task):
        # Test: Descargar resultado exitosamente
        # Arrange
        from app.routers.vision import get_async_db, get_minio_service
        
        async def override_get_db():
            mock_db = AsyncMock()
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = completed_task
            mock_db.execute.return_value = mock_result
            yield mock_db
        
        def override_minio_service():
            mock_minio = Mock()
            mock_minio.get_file.return_value = b"processed image data"
            return mock_minio
        
        app.dependency_overrides[get_async_db] = override_get_db
        app.dependency_overrides[get_minio_service] = override_minio_service
        
        try:
            # Act
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    f"/api/v1/vision/tasks/{completed_task.id}/result"
                )
            
            # Assert
            assert response.status_code == 200
            assert response.content == b"processed image data"
            assert "attachment" in response.headers["content-disposition"]
        finally:
            app.dependency_overrides.clear()
    
    @pytest.mark.asyncio
    async def test_download_result_task_not_completed(self, mock_task):
        # Test: Intentar descargar de tarea no completada
        # Arrange
        from app.routers.vision import get_async_db
        
        async def override_get_db():
            mock_db = AsyncMock()
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = mock_task
            mock_db.execute.return_value = mock_result
            yield mock_db
        
        app.dependency_overrides[get_async_db] = override_get_db
        
        try:
            # Act
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    f"/api/v1/vision/tasks/{mock_task.id}/result"
                )
            
            # Assert
            assert response.status_code == 400
            assert "completada" in response.json()["detail"].lower()
        finally:
            app.dependency_overrides.clear()
    
    @pytest.mark.asyncio
    async def test_download_result_task_not_found(self):
        # Test: Tarea no existe al intentar descargar
        # Arrange
        from app.routers.vision import get_async_db
        
        async def override_get_db():
            mock_db = AsyncMock()
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = None
            mock_db.execute.return_value = mock_result
            yield mock_db
        
        app.dependency_overrides[get_async_db] = override_get_db
        
        fake_uuid = uuid4()
        
        try:
            # Act
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    f"/api/v1/vision/tasks/{fake_uuid}/result"
                )
            
            # Assert
            assert response.status_code == 404
        finally:
            app.dependency_overrides.clear()
        
        # Assert
        assert response.status_code == 404
