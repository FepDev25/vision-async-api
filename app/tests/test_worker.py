import pytest
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4
import numpy as np
from app.worker import process_image
from app.models import Task, TaskStatus


class TestProcessImageWorker:
    """Tests para la función process_image del worker"""
    
    @patch('app.worker.SessionLocalSync')
    @patch('app.worker.MinioService')
    @patch('app.worker.cv2')
    def test_process_image_success(self, mock_cv2, mock_minio_service, mock_session):
        """Test: Procesamiento exitoso de imagen"""
        # Arrange
        task_id = str(uuid4())
        
        # Mock de la tarea
        mock_task = Mock(spec=Task)
        mock_task.id = task_id
        mock_task.filename = "test_image.jpg"
        mock_task.status = TaskStatus.PENDING
        
        # Mock de la sesión de BD
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_task
        mock_session.return_value.__enter__.return_value = mock_db
        mock_session.return_value.__exit__.return_value = None
        
        # Mock de MinIO
        mock_minio_instance = Mock()
        mock_minio_instance.get_file.return_value = b"fake image data"
        mock_minio_instance.upload_file.return_value = "processed_test_image.png"
        mock_minio_service.return_value = mock_minio_instance
        
        # Mock de OpenCV
        fake_image = np.zeros((100, 100, 3), dtype=np.uint8)
        fake_gray = np.zeros((100, 100), dtype=np.uint8)
        fake_edges = np.zeros((100, 100), dtype=np.uint8)
        fake_buffer = np.zeros((1000, 1), dtype=np.uint8)
        
        mock_cv2.imdecode.return_value = fake_image
        mock_cv2.cvtColor.return_value = fake_gray
        mock_cv2.Canny.return_value = fake_edges
        mock_cv2.imencode.return_value = (True, fake_buffer)
        
        # Act
        result = process_image(task_id)
        
        # Assert
        assert result is True
        assert mock_task.status == TaskStatus.COMPLETED
        assert mock_task.result is not None
        assert "processed_file" in mock_task.result
        assert mock_task.result["processed_file"] == "processed_test_image.png"
        mock_db.commit.assert_called()
        mock_minio_instance.get_file.assert_called_once_with("test_image.jpg")
        mock_minio_instance.upload_file.assert_called_once()
    
    @patch('app.worker.SessionLocalSync')
    def test_process_image_task_not_found(self, mock_session):
        """Test: Tarea no encontrada"""
        # Arrange
        task_id = str(uuid4())
        
        # Mock de la sesión de BD
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_session.return_value.__enter__.return_value = mock_db
        mock_session.return_value.__exit__.return_value = None
        
        # Act
        result = process_image(task_id)
        
        # Assert
        assert result is False
    
    @patch('app.worker.SessionLocalSync')
    @patch('app.worker.MinioService')
    def test_process_image_minio_download_error(self, mock_minio_service, mock_session):
        """Test: Error al descargar de MinIO"""
        # Arrange
        task_id = str(uuid4())
        
        # Mock de la tarea
        mock_task = Mock(spec=Task)
        mock_task.id = task_id
        mock_task.filename = "test_image.jpg"
        mock_task.status = TaskStatus.PENDING
        
        # Mock de la sesión de BD
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_task
        mock_session.return_value.__enter__.return_value = mock_db
        mock_session.return_value.__exit__.return_value = None
        
        # Mock de MinIO con error
        from app.services.storage import MinioServiceError
        mock_minio_instance = Mock()
        mock_minio_instance.get_file.side_effect = MinioServiceError("Download failed")
        mock_minio_service.return_value = mock_minio_instance
        
        # Act
        result = process_image(task_id)
        
        # Assert
        assert result is False
        assert mock_task.status == TaskStatus.FAILED
        assert mock_task.result is not None
        assert "error" in mock_task.result
        mock_db.commit.assert_called()
    
    @patch('app.worker.SessionLocalSync')
    @patch('app.worker.MinioService')
    @patch('app.worker.cv2')
    def test_process_image_opencv_decode_error(self, mock_cv2, mock_minio_service, mock_session):
        """Test: Error al decodificar imagen con OpenCV"""
        # Arrange
        task_id = str(uuid4())
        
        # Mock de la tarea
        mock_task = Mock(spec=Task)
        mock_task.id = task_id
        mock_task.filename = "test_image.jpg"
        mock_task.status = TaskStatus.PENDING
        
        # Mock de la sesión de BD
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_task
        mock_session.return_value.__enter__.return_value = mock_db
        mock_session.return_value.__exit__.return_value = None
        
        # Mock de MinIO
        mock_minio_instance = Mock()
        mock_minio_instance.get_file.return_value = b"fake image data"
        mock_minio_service.return_value = mock_minio_instance
        
        # Mock de OpenCV que retorna None (error de decodificación)
        mock_cv2.imdecode.return_value = None
        
        # Act
        result = process_image(task_id)
        
        # Assert
        assert result is False
        assert mock_task.status == TaskStatus.FAILED
        assert mock_task.result is not None
        assert "error" in mock_task.result
        assert "decodificar" in mock_task.result["error"].lower()
        mock_db.commit.assert_called()
    
    @patch('app.worker.SessionLocalSync')
    @patch('app.worker.MinioService')
    @patch('app.worker.cv2')
    def test_process_image_opencv_encode_error(self, mock_cv2, mock_minio_service, mock_session):
        """Test: Error al codificar imagen con OpenCV"""
        # Arrange
        task_id = str(uuid4())
        
        # Mock de la tarea
        mock_task = Mock(spec=Task)
        mock_task.id = task_id
        mock_task.filename = "test_image.jpg"
        mock_task.status = TaskStatus.PENDING
        
        # Mock de la sesión de BD
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_task
        mock_session.return_value.__enter__.return_value = mock_db
        mock_session.return_value.__exit__.return_value = None
        
        # Mock de MinIO
        mock_minio_instance = Mock()
        mock_minio_instance.get_file.return_value = b"fake image data"
        mock_minio_service.return_value = mock_minio_instance
        
        # Mock de OpenCV con error en encode
        fake_image = np.zeros((100, 100, 3), dtype=np.uint8)
        fake_gray = np.zeros((100, 100), dtype=np.uint8)
        fake_edges = np.zeros((100, 100), dtype=np.uint8)
        
        mock_cv2.imdecode.return_value = fake_image
        mock_cv2.cvtColor.return_value = fake_gray
        mock_cv2.Canny.return_value = fake_edges
        mock_cv2.imencode.return_value = (False, None)  # Fallo en encode
        
        # Act
        result = process_image(task_id)
        
        # Assert
        assert result is False
        assert mock_task.status == TaskStatus.FAILED
        assert mock_task.result is not None
        assert "error" in mock_task.result
        assert "codificar" in mock_task.result["error"].lower()
        mock_db.commit.assert_called()
    
    @patch('app.worker.SessionLocalSync')
    @patch('app.worker.MinioService')
    @patch('app.worker.cv2')
    def test_process_image_minio_upload_error(self, mock_cv2, mock_minio_service, mock_session):
        """Test: Error al subir imagen procesada a MinIO"""
        # Arrange
        task_id = str(uuid4())
        
        # Mock de la tarea
        mock_task = Mock(spec=Task)
        mock_task.id = task_id
        mock_task.filename = "test_image.jpg"
        mock_task.status = TaskStatus.PENDING
        
        # Mock de la sesión de BD
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_task
        mock_session.return_value.__enter__.return_value = mock_db
        mock_session.return_value.__exit__.return_value = None
        
        # Mock de MinIO con error en upload
        from app.services.storage import MinioServiceError
        mock_minio_instance = Mock()
        mock_minio_instance.get_file.return_value = b"fake image data"
        mock_minio_instance.upload_file.side_effect = MinioServiceError("Upload failed")
        mock_minio_service.return_value = mock_minio_instance
        
        # Mock de OpenCV
        fake_image = np.zeros((100, 100, 3), dtype=np.uint8)
        fake_gray = np.zeros((100, 100), dtype=np.uint8)
        fake_edges = np.zeros((100, 100), dtype=np.uint8)
        fake_buffer = np.zeros((1000, 1), dtype=np.uint8)
        
        mock_cv2.imdecode.return_value = fake_image
        mock_cv2.cvtColor.return_value = fake_gray
        mock_cv2.Canny.return_value = fake_edges
        mock_cv2.imencode.return_value = (True, fake_buffer)
        
        # Act
        result = process_image(task_id)
        
        # Assert
        assert result is False
        assert mock_task.status == TaskStatus.FAILED
        assert mock_task.result is not None
        assert "error" in mock_task.result
        mock_db.commit.assert_called()
    
    @patch('app.worker.SessionLocalSync')
    @patch('app.worker.MinioService')
    @patch('app.worker.cv2')
    def test_process_image_updates_status_to_processing(self, mock_cv2, mock_minio_service, mock_session):
        """Test: Verifica que el status se actualiza a PROCESSING al inicio"""
        # Arrange
        task_id = str(uuid4())
        
        # Mock de la tarea
        mock_task = Mock(spec=Task)
        mock_task.id = task_id
        mock_task.filename = "test_image.jpg"
        mock_task.status = TaskStatus.PENDING
        
        # Mock de la sesión de BD
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_task
        mock_session.return_value.__enter__.return_value = mock_db
        mock_session.return_value.__exit__.return_value = None
        
        # Mock de MinIO
        mock_minio_instance = Mock()
        mock_minio_instance.get_file.return_value = b"fake image data"
        mock_minio_instance.upload_file.return_value = "processed_test_image.png"
        mock_minio_service.return_value = mock_minio_instance
        
        # Mock de OpenCV
        fake_image = np.zeros((100, 100, 3), dtype=np.uint8)
        fake_gray = np.zeros((100, 100), dtype=np.uint8)
        fake_edges = np.zeros((100, 100), dtype=np.uint8)
        fake_buffer = np.zeros((1000, 1), dtype=np.uint8)
        
        mock_cv2.imdecode.return_value = fake_image
        mock_cv2.cvtColor.return_value = fake_gray
        mock_cv2.Canny.return_value = fake_edges
        mock_cv2.imencode.return_value = (True, fake_buffer)
        
        # Act
        process_image(task_id)
        
        # Assert
        # Verificar que el status pasó por PROCESSING antes de COMPLETED
        assert mock_db.commit.call_count >= 2  # Al menos 2 commits: PROCESSING y COMPLETED
        # El status final debe ser COMPLETED
        assert mock_task.status == TaskStatus.COMPLETED
