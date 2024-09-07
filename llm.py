from time import sleep
import google.generativeai as genai

keys = [] # add your keys in the list

safety_level = {
    0: "BLOCK_NONE",
    1: "BLOCK_ONLY_HIGH",
    2: "BLOCK_MEDIUM_AND_ABOVE",
    3: "BLOCK_LOW_AND_ABOVE"
}

# change keys after every two calls to use the free quota
idx = 0


class LLM:
    def __init__(self, temperature, model_name) -> None:
        generation_config = {
            "temperature": temperature,
            "response_mime_type": "text/plain",
        }
        self.temperature = temperature
        self.model_name = model_name

        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config,
        )
        
    def generate(self, prompt, image_path, safety_rating):
        global idx
        if idx % 2 == 0: 
            genai.configure(api_key=keys[idx%len(keys)])
            self.__init__(self.temperature, self.model_name) 
        meme_img = genai.upload_file(path=image_path,
                                display_name="Meme-image")
        
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": safety_level[safety_rating],
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": safety_level[safety_rating],
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": safety_level[safety_rating],
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": safety_level[safety_rating],
            },
        ]

        # to handle resource exhaustion and other api errors
        while True:
            try:
                model = self.model
                response = model.generate_content([meme_img, prompt],
                                                  safety_settings=safety_settings)
                idx += 1
                return response.text
            except Exception as e:
                print(e)
                sleep(5)
