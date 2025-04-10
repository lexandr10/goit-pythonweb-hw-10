import cloudinary
import cloudinary.uploader


class UploadFileService:
    def __init__(self, cloud_name, api_key, api_secret):
        self.cloud_name = cloud_name
        self.api_key = api_key
        self.api_secret = api_secret

        cloudinary.config(
            cloud_name=self.cloud_name, api_key=self.api_key, api_secret=self.api_secret
        )

    @staticmethod
    def upload_file(file, username):
        public_id = f"Restapi/{username}"
        r = cloudinary.uploader.upload(file, public_id=public_id, overwrite=True)
        src_url = cloudinary.CloudinaryImage(public_id).build_url(
            width=250,
            height=250,
            crop="fill",
            gravity="face",
            radius=20,
            version=r.get("version"),
        )
        return src_url
