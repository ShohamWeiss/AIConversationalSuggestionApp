from operator import truediv
from transformers import pipeline, AutoTokenizer
from Conversation import Conversation

class QA():
    def __init__(self):
        self.model = pipeline("question-answering")
        
    def generate_options(self, conversation:Conversation, context:str) -> str:
        '''Generates options from a conversation'''  
        question = conversation.pop()
        result = self.model(question=question[0], context=context)
        options = []
        # check if result is a list
        if (not isinstance(result, list)):
            result = [result]
            
        for option in result:
            if option["score"] > 0.6:
                options.append(option["answer"])        
        return options
    
if __name__=="__main__":
    conv = Conversation()    
    qa = QA()
    
    while(True):
        c = """Jhonny has two balloons, a blue and a red balloon.
            Jhonny fell down the stairs yesterday and broke his arm"""
        n = input("Question:")
        conv.add("Them", n)
        options = qa.generate_options(conv, c)
        print(options)
