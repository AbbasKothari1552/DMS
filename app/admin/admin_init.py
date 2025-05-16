from sqladmin import Admin
from app.db.session import engine
from app.admin.views import FileMetadataAdmin, TextMetadataAdmin, ChunkMetadataAdmin

def setup_admin(app):
    admin = Admin(app, engine)
    admin.add_view(FileMetadataAdmin)
    admin.add_view(TextMetadataAdmin)
    admin.add_view(ChunkMetadataAdmin)
