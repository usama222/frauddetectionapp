class Config:
    SECRET_KEY = "dev-secret-key"
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123@localhost/fraudapp_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False