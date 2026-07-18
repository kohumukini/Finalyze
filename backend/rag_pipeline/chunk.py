import re
from ..config import MIN_CHUNK_SIZE, MAX_CHUNK_SIZE, OVERLAP_SIZE

# Chunker
# Args - Text, Document of Origin Name
# Return - List of objects 
def chunk_doc(text):
    chunks = []
    #document_name = document.lower().replace(" ", "_")
    counter = 0
    start = 0
    
    sentence_pattern = r'[.!?][\"\']?\s*$'
    
    while start < len(text): 
        end = start + MAX_CHUNK_SIZE
        chunk = text[start:end]
        sentence_ends = list(re.finditer(sentence_pattern, chunk))
        
        if sentence_ends: 
            last_end = sentence_ends[-1]
        else: 
            return None
        
        print(chunk[0:last_end.first()])
        
        start = last_end.first()
        
sentence = "Ecologically, the integration of green infrastructure into city planning is a powerful tool against climate change. Trees and vegetation act as natural carbon sinks, absorbing greenhouse gases while trapping airborne pollutants like particulate matter. Furthermore, the foliage canopy significantly lowers local temperatures through shade and evapotranspiration. For instance, according to Penn State Extension, the strategic placement of shade trees can reduce urban air temperatures, which lowers energy demand for air conditioning and drastically cuts municipal carbon footprints.Beyond ecological preservation, urban green spaces are fundamental to human psychological well-being. Living in heavily built environments often correlates with heightened levels of stress, anxiety, and mental fatigue. Access to nature, commonly referred to in environmental psychology as nature therapy or shinrin-yoku, has been clinically proven to lower cortisol levels, decrease blood pressure, and improve cognitive function. A study published by the American Psychological Association highlights that spending just a few hours a week in green spaces can lead to profound mental health benefits, including enhanced mood and improved attention span.Additionally, urban parks and community gardens function as vital social hubs that foster civic engagement and equity. They provide democratic, free-access areas where people from diverse socioeconomic backgrounds can exercise, socialize, and participate in community events. This social cohesion is particularly crucial in sprawling metropolises where isolation and disconnection are common byproducts of urban density. By breaking up the monotony of steel and concrete, these shared environments encourage physical activity and strengthen a community's collective identity.In conclusion, the integration of green spaces into urban design is much more than an aesthetic enhancement; it is a necessity for sustainable living. As global populations urbanize, prioritizing the development and preservation of these natural sanctuaries will be critical. Ultimately, protecting our urban canopies ensures that city dwellers can thrive both physically and mentally, bridging the widening gap between human civilization and the natural world."

chunk_doc(sentence)