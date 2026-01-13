import pytest
from unittest.mock import Mock, patch, MagicMock
from botocore.exceptions import ClientError, BotoCoreError
from app.services.storage import MinioService, MinioServiceError


class TestMinioService:
    # Tests para la clase MinioService
    
    @patch('app.services.storage.boto3.client')
    def test_init_success(self, mock_boto3_client):
        # Test: Inicialización exitosa con bucket existente
        # Arrange
        mock_s3_client = Mock()
        mock_boto3_client.return_value = mock_s3_client
        mock_s3_client.head_bucket.return_value = {}
        
        # Act
        service = MinioService()
        
        # Assert
        assert service.client == mock_s3_client
        assert service.bucket_name is not None
        mock_s3_client.head_bucket.assert_called_once()
    
    @patch('app.services.storage.boto3.client')
    def test_init_bucket_not_exists(self, mock_boto3_client):
        # Test: Falla cuando el bucket no existe (404)
        # Arrange
        mock_s3_client = Mock()
        mock_boto3_client.return_value = mock_s3_client
        
        error_response = {'Error': {'Code': '404'}}
        mock_s3_client.head_bucket.side_effect = ClientError(
            error_response, 'HeadBucket'
        )
        
        # Act & Assert
        with pytest.raises(MinioServiceError) as exc_info:
            MinioService()
        
        assert "no existe" in str(exc_info.value)
        assert "infraestructura" in str(exc_info.value)
    
    @patch('app.services.storage.boto3.client')
    def test_init_connection_error(self, mock_boto3_client):
        # Test: Error de conexión al inicializar
        # Arrange
        mock_s3_client = Mock()
        mock_boto3_client.return_value = mock_s3_client
        mock_s3_client.head_bucket.side_effect = BotoCoreError()
        
        # Act & Assert
        with pytest.raises(MinioServiceError) as exc_info:
            MinioService()
        
        assert "Error de conexión" in str(exc_info.value)
    
    @patch('app.services.storage.boto3.client')
    def test_init_client_error_non_404(self, mock_boto3_client):
        # Test: Error de cliente (no 404) al verificar bucket
        # Arrange
        mock_s3_client = Mock()
        mock_boto3_client.return_value = mock_s3_client
        
        error_response = {'Error': {'Code': '403'}}
        mock_s3_client.head_bucket.side_effect = ClientError(
            error_response, 'HeadBucket'
        )
        
        # Act & Assert
        with pytest.raises(MinioServiceError) as exc_info:
            MinioService()
        
        assert "Error al verificar el bucket" in str(exc_info.value)
    
    @patch('app.services.storage.boto3.client')
    def test_init_unexpected_error(self, mock_boto3_client):
        # Test: Error inesperado al inicializar
        # Arrange
        mock_boto3_client.side_effect = Exception("Error inesperado")
        
        # Act & Assert
        with pytest.raises(MinioServiceError) as exc_info:
            MinioService()
        
        assert "Error inesperado" in str(exc_info.value)
    
    @patch('app.services.storage.boto3.client')
    def test_upload_file_success(self, mock_boto3_client):
        # Test: Subida exitosa de archivo
        # Arrange
        mock_s3_client = Mock()
        mock_boto3_client.return_value = mock_s3_client
        mock_s3_client.head_bucket.return_value = {}
        mock_s3_client.put_object.return_value = {}
        
        service = MinioService()
        file_content = b"contenido de prueba"
        file_name = "test_image.jpg"
        
        # Act
        result = service.upload_file(file_content, file_name)
        
        # Assert
        assert result == file_name
        mock_s3_client.put_object.assert_called_once()
        call_args = mock_s3_client.put_object.call_args
        assert call_args.kwargs['Key'] == file_name
        assert call_args.kwargs['Body'] == file_content
    
    @patch('app.services.storage.boto3.client')
    def test_upload_file_client_error(self, mock_boto3_client):
        # Test: Error de cliente al subir archivo
        # Arrange
        mock_s3_client = Mock()
        mock_boto3_client.return_value = mock_s3_client
        mock_s3_client.head_bucket.return_value = {}
        
        error_response = {'Error': {'Code': '500'}}
        mock_s3_client.put_object.side_effect = ClientError(
            error_response, 'PutObject'
        )
        
        service = MinioService()
        
        # Act & Assert
        with pytest.raises(MinioServiceError) as exc_info:
            service.upload_file(b"test", "test.jpg")
        
        assert "Error al subir el archivo" in str(exc_info.value)
    
    @patch('app.services.storage.boto3.client')
    def test_upload_file_connection_error(self, mock_boto3_client):
        # Test: Error de conexión al subir archivo
        # Arrange
        mock_s3_client = Mock()
        mock_boto3_client.return_value = mock_s3_client
        mock_s3_client.head_bucket.return_value = {}
        mock_s3_client.put_object.side_effect = BotoCoreError()
        
        service = MinioService()
        
        # Act & Assert
        with pytest.raises(MinioServiceError) as exc_info:
            service.upload_file(b"test", "test.jpg")
        
        assert "Error de conexión" in str(exc_info.value)
    
    @patch('app.services.storage.boto3.client')
    def test_upload_file_unexpected_error(self, mock_boto3_client):
        # Test: Error inesperado al subir archivo
        # Arrange
        mock_s3_client = Mock()
        mock_boto3_client.return_value = mock_s3_client
        mock_s3_client.head_bucket.return_value = {}
        mock_s3_client.put_object.side_effect = Exception("Error raro")
        
        service = MinioService()
        
        # Act & Assert
        with pytest.raises(MinioServiceError) as exc_info:
            service.upload_file(b"test", "test.jpg")
        
        assert "Error inesperado" in str(exc_info.value)
