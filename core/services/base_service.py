class BaseService:
    @classmethod
    def validate_data(cls, data, required_fields):
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Campo requerido: {field}")
        return True
