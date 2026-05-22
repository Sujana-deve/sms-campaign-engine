"""with the help of this the main runner file doesn't 
need to know which gatway,simulate ,or real one like 
sparrow is being run using the abstractmethod"""
from abc import ABC, abstractmethod
class BaseGateway(ABC):
    @abstractmethod
    def send(self,phone,message):
        pass