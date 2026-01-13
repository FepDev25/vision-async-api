import boto3
from botocore.exceptions import ClientError, BotoCoreError
from app.core.config import settings


class MinioServiceError(Exception):
    # Excepción personalizada para errores del servicio MinIO
    pass


class MinioService:
    # Servicio para interactuar con MinIO usando boto3
    
    # Constructor: Inicializa el cliente de boto3 (s3) y verifica que el bucket exista
    # Raises: MinioServiceError: Si hay un error al conectar o si el bucket no existe
    def __init__(self):
        try:
            # Inicializar cliente boto3 para MinIO
            self.client = boto3.client(
                's3',
                endpoint_url=settings.MINIO_ENDPOINT,
                aws_access_key_id=settings.MINIO_ACCESS_KEY,
                aws_secret_access_key=settings.MINIO_SECRET_KEY,
                use_ssl=settings.MINIO_SECURE,
                verify=settings.MINIO_SECURE
            )
            self.bucket_name = settings.MINIO_BUCKET_NAME
            
            # Verificar que el bucket existe
            self._verify_bucket_exists()
            
        except (ClientError, BotoCoreError) as e:
            raise MinioServiceError(
                f"Error al inicializar el cliente MinIO: {str(e)}"
            ) from e
        except Exception as e:
            raise MinioServiceError(
                f"Error inesperado al inicializar MinioService: {str(e)}"
            ) from e
    
    # Verifica que el bucket configurado existe en MinIO.
    # Raises: MinioServiceError: Si el bucket no existe
    def _verify_bucket_exists(self) -> None:
        try:
            self.client.head_bucket(Bucket=self.bucket_name)

        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code == '404':
                raise MinioServiceError(
                    f"El bucket '{self.bucket_name}' no existe. "
                    "Asegúrate de que la infraestructura esté configurada correctamente."
                ) from e
            else:
                raise MinioServiceError(
                    f"Error al verificar el bucket '{self.bucket_name}': {str(e)}"
                ) from e
        except BotoCoreError as e:
            raise MinioServiceError(
                f"Error de conexión al verificar el bucket: {str(e)}"
            ) from e
    
    # Sube un archivo al bucket de MinIO
    # Args:
    #      file_content: Contenido del archivo en bytes
    #      file_name: Nombre con el que se guardará el archivo
    # Returns:
    #       str: Nombre del archivo guardado en el bucket
    # Raises:
    #       MinioServiceError: Si hay un error al subir el archivo
    def upload_file(self, file_content: bytes, file_name: str) -> str:
        try:
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=file_name,
                Body=file_content
            )
            return file_name
            
        except ClientError as e:
            raise MinioServiceError(
                f"Error al subir el archivo '{file_name}' a MinIO: {str(e)}"
            ) from e
        except BotoCoreError as e:
            raise MinioServiceError(
                f"Error de conexión al subir el archivo '{file_name}': {str(e)}"
            ) from e
        except Exception as e:
            raise MinioServiceError(
                f"Error inesperado al subir el archivo '{file_name}': {str(e)}"
            ) from e
