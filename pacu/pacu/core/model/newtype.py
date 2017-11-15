from sqlalchemy import TypeDecorator, Text

# class NewType(TypeDecorator):
#     impl = Text
#     def process_bind_param(self, value, dialect):
#         return value
#     def process_result_value(self, value, dialect):
#         return value

class ListFloatText(TypeDecorator):
    impl = Text
    type = float
    def process_result_value(self, value, dialect):
        return [self.type(x) for x in value.split(',')]

class ListIntText(ListFloatText):
    type = int
