from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

engine = create_engine("sqlite:///database.db")

Session = sessionmaker(engine)


class Base(DeclarativeBase):
    pass


class ChatUser(Base):
    __tablename__ = "chat_users"
    chat_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(primary_key=True)
    agreed_with_rules: Mapped[bool] = mapped_column(default=False)


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
