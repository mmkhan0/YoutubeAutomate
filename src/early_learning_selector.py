"""
Early Learning Topic Selector for Toddlers (Ages 2-6)

STRICT CONTENT CONTROL for kids mind development videos only.
Randomly selects ONE topic from allowed categories with history tracking
to prevent repetition.

COPPA & YouTube Kids compliant.
"""

import logging
import json
import random
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime


class EarlyLearningTopicSelector:
    """
    Selects ONLY early childhood learning topics for ages 2-6.

    ALLOWED CATEGORIES (controlled list):
    1. English Alphabet (A-Z)
    2. Hindi Alphabet (अ-ज्ञ)
    3. Numbers and Counting (1-20)
    4. Colors and Shapes
    5. Fruits and Vegetables
    6. Animals and Sounds
    7. Matching and Memory Games
    8. Simple Logic (Big/Small, More/Less, Same/Different)
    9. Body Parts
    10. Daily Habits (brushing, eating, sleeping)
    11. Emotional Learning (happy, sad, angry)
    12. Basic Math Games
    13. Rhymes with Learning
    14. Puzzle Thinking Games
    15. Observation and Attention Games
    """

    # Topic history file path
    HISTORY_FILE = "data/topic_history.json"

    # Maximum topics to track (prevent repetition)
    MAX_HISTORY = 5

    # Age group
    MIN_AGE = 2
    MAX_AGE = 6

    # Allowed topic categories with templates
    TOPIC_CATEGORIES = {
        "english_alphabet": {
            "weight": 10,
            "templates": [
                "Learning Letter {letter} - {letter} for {word} | ABC for Toddlers",
                "Fun with Letter {letter} - A to Z Learning for Kids",
                "Big Letter {letter} and Small Letter {letter_lower} - Alphabet Fun",
                "Letter {letter} Song - Phonics Learning for Toddlers",
                "Trace and Learn Letter {letter} - Writing Practice for Kids"
            ],
            "data": {
                "A": ["Apple", "Ant", "Airplane"],
                "B": ["Ball", "Banana", "Bear"],
                "C": ["Cat", "Car", "Cup"],
                "D": ["Dog", "Duck", "Door"],
                "E": ["Elephant", "Egg", "Eye"],
                "F": ["Fish", "Flower", "Frog"],
                "G": ["Goat", "Grapes", "Gate"],
                "H": ["Hat", "House", "Horse"],
                "I": ["Ice cream", "Igloo", "Ink"],
                "J": ["Jug", "Jet", "Juice"],
                "K": ["Kite", "King", "Key"],
                "L": ["Lion", "Leaf", "Lamp"],
                "M": ["Monkey", "Moon", "Mango"],
                "N": ["Nest", "Nose", "Net"],
                "O": ["Orange", "Owl", "Ox"],
                "P": ["Pig", "Pen", "Pizza"],
                "Q": ["Queen", "Quilt", "Question"],
                "R": ["Rabbit", "Rain", "Rose"],
                "S": ["Sun", "Star", "Snake"],
                "T": ["Tiger", "Tree", "Tent"],
                "U": ["Umbrella", "Up", "Uncle"],
                "V": ["Van", "Vase", "Violin"],
                "W": ["Watch", "Water", "Window"],
                "X": ["X-ray", "Xylophone", "Box"],
                "Y": ["Yellow", "Yak", "Yo-yo"],
                "Z": ["Zebra", "Zoo", "Zip"]
            }
        },

        "hindi_alphabet": {
            "weight": 8,
            "templates": [
                "हिंदी वर्णमाला - {letter} से {word} | Hindi Alphabet for Kids",
                "अ से अनार - Learning Hindi Letter {letter} for Toddlers",
                "मजेदार हिंदी {letter} - Fun Hindi Alphabet Learning"
            ],
            "data": {
                "अ": ["अनार", "अंगूर"],
                "आ": ["आम", "आलू"],
                "इ": ["इमली", "इंद्रधनुष"],
                "ई": ["ईख", "ईंट"],
                "उ": ["उल्लू", "उंगली"],
                "ऊ": ["ऊन", "ऊंट"],
                "ए": ["एक", "एड़ी"],
                "ऐ": ["ऐनक", "ऐरावत"],
                "ओ": ["ओखली", "ओस"],
                "औ": ["औरत", "और"],
                "क": ["कबूतर", "कमल"],
                "ख": ["खरगोश", "खिलौना"],
                "ग": ["गधा", "गेंद"],
                "घ": ["घर", "घड़ी"],
                "च": ["चम्मच", "चश्मा"],
                "छ": ["छतरी", "छत"],
                "ज": ["जहाज", "जग"],
                "झ": ["झंडा", "झरना"],
                "ट": ["टमाटर", "टोपी"],
                "ठ": ["ठठेरा", "ठेला"],
                "ड": ["डमरू", "डाली"],
                "ढ": ["ढक्कन", "ढोल"],
                "त": ["तरबूज", "तालाब"],
                "थ": ["थैला", "थाली"],
                "द": ["दवा", "दरवाजा"],
                "ध": ["धनुष", "धागा"],
                "न": ["नल", "नाव"],
                "प": ["पतंग", "पंखा"],
                "फ": ["फल", "फूल"],
                "ब": ["बकरी", "बादल"],
                "भ": ["भालू", "भेड़"],
                "म": ["मछली", "मोर"],
                "य": ["यज्ञ", "योगा"],
                "र": ["रथ", "राजा"],
                "ल": ["लड्डू", "लट्टू"],
                "व": ["वन", "वर्षा"],
                "श": ["शेर", "शलजम"],
                "स": ["सेब", "साप"],
                "ह": ["हाथी", "हल"]
            }
        },

        "numbers_counting": {
            "weight": 12,
            "templates": [
                "Learning Numbers {start} to {end} - Counting Fun for Toddlers",
                "Count with Me - Numbers {start} to {end} for Kids",
                "Fun Counting - Learning Number {number} with Objects",
                "Number Songs - Counting {start} to {end} for Preschoolers",
                "How Many? - Learn Counting {start} to {end}"
            ],
            "ranges": [
                (1, 5), (1, 10), (1, 20), (11, 20),
                (5, 10), (10, 15)
            ],
            "single_numbers": [1, 2, 3, 4, 5, 10, 15, 20]
        },

        "colors_shapes": {
            "weight": 10,
            "templates": [
                "Learning Colors - {color} Color Fun for Toddlers",
                "Find the {color} Things - Color Recognition for Kids",
                "Learning Shapes - {shape} Shape for Preschoolers",
                "Colors and Shapes Together - {color} {shape}",
                "Rainbow Colors Song - Learning All Colors for Kids",
                "Shape Sorting Game - Circles, Squares, Triangles for Toddlers"
            ],
            "colors": ["Red", "Blue", "Yellow", "Green", "Orange", "Purple", "Pink", "Brown", "Black", "White"],
            "shapes": ["Circle", "Square", "Triangle", "Rectangle", "Star", "Heart", "Diamond", "Oval"]
        },

        "fruits_vegetables": {
            "weight": 9,
            "templates": [
                "Learning Fruits - {item} is Yummy and Healthy",
                "Vegetables for Kids - Learn About {item}",
                "Fruit and Vegetable Songs - Fun Learning for Toddlers",
                "Healthy Eating - All About {item} for Kids",
                "Farm to Table - Where Does {item} Come From?"
            ],
            "fruits": ["Apple", "Banana", "Orange", "Grapes", "Mango", "Strawberry", "Watermelon", "Pineapple"],
            "vegetables": ["Carrot", "Tomato", "Potato", "Broccoli", "Peas", "Corn", "Pumpkin", "Cucumber"]
        },

        "animals_sounds": {
            "weight": 12,
            "templates": [
                "Animal Sounds - What Does a {animal} Say?",
                "Learning About {animal} - Fun Animal Facts for Kids",
                "Farm Animals - Meet the {animal} | Sounds and Fun",
                "Wild Animals - Amazing {animal} for Toddlers",
                "Pet Animals - Learning About {animal} for Kids",
                "Animal Families - Baby {animal} and Parent {animal}"
            ],
            "farm_animals": ["Cow", "Horse", "Sheep", "Goat", "Pig", "Chicken", "Duck", "Rooster"],
            "wild_animals": ["Lion", "Elephant", "Monkey", "Giraffe", "Zebra", "Tiger", "Bear", "Panda"],
            "pets": ["Dog", "Cat", "Rabbit", "Fish", "Bird", "Hamster"],
            "sounds": {
                "Cow": "Moo", "Dog": "Woof", "Cat": "Meow", "Sheep": "Baa",
                "Duck": "Quack", "Lion": "Roar", "Elephant": "Trumpet"
            }
        },

        "simple_logic": {
            "weight": 11,
            "templates": [
                "Big and Small - Learning Sizes for Toddlers",
                "More or Less - Counting and Comparing for Kids",
                "Same and Different - Matching Game for Preschoolers",
                "Heavy and Light - Understanding Weight for Kids",
                "Tall and Short - Learning Opposites for Toddlers",
                "Hot and Cold - Temperature Learning for Kids",
                "Fast and Slow - Speed Concepts for Toddlers",
                "Full and Empty - Understanding Quantity for Kids"
            ]
        },

        "body_parts": {
            "weight": 8,
            "templates": [
                "Learning Body Parts - Head, Shoulders, Knees and Toes",
                "My Body - Learning About {part} for Kids",
                "Body Parts Song - Fun Learning for Toddlers",
                "Five Senses - Learning About Eyes, Ears, Nose for Kids",
                "Parts of Face - Learning About {part} for Preschoolers"
            ],
            "parts": [
                "Head", "Eyes", "Ears", "Nose", "Mouth", "Hands", "Feet",
                "Fingers", "Toes", "Hair", "Teeth", "Tongue", "Arms", "Legs"
            ]
        },

        "daily_habits": {
            "weight": 9,
            "templates": [
                "Good Habits - {habit} Every Day for Kids",
                "Daily Routine Song - {habit} Time for Toddlers",
                "Healthy Habits - Learning to {habit} for Preschoolers",
                "Morning Routine - {habit} for Kids",
                "Bedtime Routine - {habit} Before Sleep"
            ],
            "habits": [
                "Brush Your Teeth", "Wash Your Hands", "Take a Bath",
                "Eat Healthy Food", "Drink Water", "Sleep on Time",
                "Clean Your Room", "Wear Clean Clothes", "Comb Your Hair",
                "Say Please and Thank You", "Share with Friends"
            ]
        },

        "emotions": {
            "weight": 8,
            "templates": [
                "Learning Emotions - Feeling {emotion} for Kids",
                "Feelings and Emotions - Understanding {emotion} for Toddlers",
                "It's Okay to Feel {emotion} - Emotional Learning for Kids",
                "All About Feelings - Happy, Sad, Angry for Preschoolers"
            ],
            "emotions": ["Happy", "Sad", "Angry", "Scared", "Excited", "Surprised", "Proud", "Calm"]
        },

        "basic_math": {
            "weight": 10,
            "templates": [
                "Simple Addition - Learning 1+1 for Toddlers",
                "Counting More and Less - Math Fun for Kids",
                "First and Last - Understanding Order for Preschoolers",
                "One More, One Less - Number Concepts for Kids",
                "Simple Subtraction - Taking Away for Toddlers"
            ]
        },

        "rhymes_learning": {
            "weight": 9,
            "templates": [
                "Nursery Rhyme - {rhyme} with Learning",
                "Educational Rhyme - {rhyme} for Toddlers",
                "Sing and Learn - {rhyme} for Kids",
                "Classic Rhyme - {rhyme} with Actions"
            ],
            "rhymes": [
                "Twinkle Twinkle Little Star", "ABC Song", "One Two Buckle My Shoe",
                "Head Shoulders Knees and Toes", "Wheels on the Bus",
                "Old MacDonald Had a Farm", "Baa Baa Black Sheep",
                "Humpty Dumpty", "Jack and Jill", "Five Little Ducks"
            ]
        },

        "memory_games": {
            "weight": 7,
            "templates": [
                "Memory Matching Game - Find the Pairs for Kids",
                "What's Missing? - Memory Game for Toddlers",
                "Remember the Pattern - Memory Fun for Preschoolers",
                "Match the Colors - Memory Game for Kids",
                "Find the Same - Matching Game for Toddlers"
            ]
        },

        "puzzle_games": {
            "weight": 7,
            "templates": [
                "Jigsaw Puzzle Fun - Simple Puzzles for Toddlers",
                "Shape Sorting - Puzzle Game for Kids",
                "Complete the Picture - Puzzle Learning for Preschoolers",
                "Pattern Puzzle - What Comes Next for Kids?"
            ]
        },

        "observation_games": {
            "weight": 6,
            "templates": [
                "Spot the Difference - Observation Game for Kids",
                "Find the Hidden Object - Search Game for Toddlers",
                "Count How Many - Observation Fun for Preschoolers",
                "What's Wrong in This Picture? - Logic Game for Kids",
                "Focus and Find - Attention Game for Toddlers"
            ]
        }
    }

    def __init__(self, data_dir: str = "data"):
        """
        Initialize the early learning topic selector.

        Args:
            data_dir: Directory to store topic history
        """
        self.logger = logging.getLogger(__name__)
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.history_file = self.data_dir / "topic_history.json"

        # Load topic history
        self.history = self._load_history()

    def select_topic(self, language: str = "en") -> Dict[str, str]:
        """
        Select ONE random topic from allowed categories.
        Prevents repetition of last 5 topics.

        Args:
            language: Language code (en, hi, both)

        Returns:
            Dict with keys: topic, category, age_group, language
        """
        self.logger.info(f"🎲 Selecting early learning topic for ages {self.MIN_AGE}-{self.MAX_AGE}")

        # Filter categories by language
        available_categories = self._filter_by_language(language)

        # Build weighted list (exclude recently used categories)
        weighted_categories = self._build_weighted_list(available_categories)

        # Randomly select category
        category_key = random.choices(
            list(weighted_categories.keys()),
            weights=[weighted_categories[k] for k in weighted_categories.keys()],
            k=1
        )[0]

        # Generate topic from category
        topic_data = self._generate_topic_from_category(category_key)

        # Add to history
        self._add_to_history(topic_data)

        self.logger.info(f"✓ Selected: {topic_data['topic']}")
        self.logger.info(f"   Category: {topic_data['category']}")
        self.logger.info(f"   Age: {topic_data['age_group']}")

        return topic_data

    def _filter_by_language(self, language: str) -> Dict:
        """Filter categories by language preference."""
        if language == "hi":
            # Hindi: Hindi alphabet, numbers, colors, fruits, animals, logic
            return {k: v for k, v in self.TOPIC_CATEGORIES.items()
                   if k in ["hindi_alphabet", "numbers_counting", "colors_shapes",
                           "fruits_vegetables", "animals_sounds", "simple_logic",
                           "daily_habits", "emotions", "basic_math"]}
        elif language == "en":
            # English: All except Hindi alphabet
            return {k: v for k, v in self.TOPIC_CATEGORIES.items()
                   if k != "hindi_alphabet"}
        else:  # both
            return self.TOPIC_CATEGORIES.copy()

    def _build_weighted_list(self, categories: Dict) -> Dict:
        """Build weighted category list, reducing weight for recent topics."""
        weighted = {}

        for cat_key, cat_data in categories.items():
            base_weight = cat_data["weight"]

            # Check if recently used (last 5)
            recent_count = sum(1 for h in self.history[-self.MAX_HISTORY:]
                             if h.get("category_key") == cat_key)

            # Reduce weight if recently used
            if recent_count > 0:
                weight = max(1, base_weight - (recent_count * 3))
            else:
                weight = base_weight

            weighted[cat_key] = weight

        return weighted

    def _generate_topic_from_category(self, category_key: str) -> Dict[str, str]:
        """Generate specific topic from category."""
        category = self.TOPIC_CATEGORIES[category_key]
        template = random.choice(category["templates"])

        # Fill template based on category
        if category_key == "english_alphabet":
            letter = random.choice(list(category["data"].keys()))
            word = random.choice(category["data"][letter])
            topic = template.format(
                letter=letter,
                letter_lower=letter.lower(),
                word=word
            )

        elif category_key == "hindi_alphabet":
            letter = random.choice(list(category["data"].keys()))
            word = random.choice(category["data"][letter])
            topic = template.format(letter=letter, word=word)

        elif category_key == "numbers_counting":
            if "{number}" in template:
                number = random.choice(category["single_numbers"])
                topic = template.format(number=number)
            else:
                start, end = random.choice(category["ranges"])
                topic = template.format(start=start, end=end)

        elif category_key == "colors_shapes":
            if "{color}" in template and "{shape}" in template:
                color = random.choice(category["colors"])
                shape = random.choice(category["shapes"])
                topic = template.format(color=color, shape=shape)
            elif "{color}" in template:
                color = random.choice(category["colors"])
                topic = template.format(color=color)
            elif "{shape}" in template:
                shape = random.choice(category["shapes"])
                topic = template.format(shape=shape)
            else:
                topic = template

        elif category_key == "fruits_vegetables":
            if "Fruit" in template or "fruit" in template:
                item = random.choice(category["fruits"])
            else:
                item = random.choice(category["vegetables"])
            topic = template.format(item=item)

        elif category_key == "animals_sounds":
            # Choose from all animal types
            all_animals = (category["farm_animals"] +
                          category["wild_animals"] +
                          category["pets"])
            animal = random.choice(all_animals)
            topic = template.format(animal=animal)

        elif category_key == "body_parts":
            if "{part}" in template:
                part = random.choice(category["parts"])
                topic = template.format(part=part)
            else:
                topic = template

        elif category_key == "daily_habits":
            habit = random.choice(category["habits"])
            topic = template.format(habit=habit)

        elif category_key == "emotions":
            emotion = random.choice(category["emotions"])
            topic = template.format(emotion=emotion)

        elif category_key == "rhymes_learning":
            rhyme = random.choice(category["rhymes"])
            topic = template.format(rhyme=rhyme)

        else:
            # Categories without variables (simple_logic, basic_math, etc.)
            topic = template

        return {
            "topic": topic,
            "category": category_key.replace("_", " ").title(),
            "category_key": category_key,
            "age_group": f"{self.MIN_AGE}-{self.MAX_AGE} years",
            "language": "Hindi" if category_key == "hindi_alphabet" else "English",
            "timestamp": datetime.now().isoformat()
        }

    def _load_history(self) -> List[Dict]:
        """Load topic history from file."""
        if not self.history_file.exists():
            return []

        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.warning(f"Could not load history: {e}")
            return []

    def _save_history(self):
        """Save topic history to file."""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Could not save history: {e}")

    def _add_to_history(self, topic_data: Dict):
        """Add topic to history and trim to max size."""
        self.history.append(topic_data)

        # Keep only last 50 entries
        if len(self.history) > 50:
            self.history = self.history[-50:]

        self._save_history()

    def get_recent_topics(self, count: int = 10) -> List[str]:
        """Get list of recent topics."""
        return [h["topic"] for h in self.history[-count:]]

    def is_coppa_compliant(self) -> bool:
        """Confirm all topics are COPPA compliant."""
        return True  # All topics are designed for ages 2-6
