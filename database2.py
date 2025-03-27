
#функция сохраняет ссылки на вопросы квиза из базы данных в модулях
def get_quiz_data(data):
    import handlers
    handlers.quiz_data = data
    import service
    service.quiz_data = data

#Асинхронный счетчик для перебора async for    
class Asyncrange:
    class __asyncrange:
        def __init__(self, *args):
            self.__iter_range = iter(range(1,*args))
        async def __anext__(self):
            try:
                return next(self.__iter_range)           
            except StopIteration as e:
                raise StopAsyncIteration(str(e))
    def __init__(self, *args):
        self.__args = args
    def __aiter__(self):
        return self.__asyncrange(*self.__args)
