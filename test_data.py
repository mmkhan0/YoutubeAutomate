"""
Test data for running automation without OpenAI API calls.

This module provides pre-written scripts and content for testing
the video creation pipeline without requiring API credits.
"""

# Test topics (kid-friendly, educational)
TEST_TOPICS = [
    "How Do Flowers Grow?",
    "Learning Colors with Rainbow Animals",
    "Why Do We Have Day and Night?",
    "The Amazing Life of Butterflies",
    "Counting to 10 with Forest Friends",
]

# Test scripts with scene descriptions
TEST_SCRIPTS = {
    "How Do Flowers Grow?": {
        "topic": "How Do Flowers Grow?",
        "total_duration": 240,
        "sections": [
            {
                "type": "intro",
                "duration": 30,
                "narration": "Hello friends! Today we're going to learn something amazing! Have you ever wondered how beautiful flowers grow? Let's discover the magic of flowers together!",
                "image_description": "A colorful garden with various blooming flowers including roses, daisies, and sunflowers, with a bright sun shining overhead"
            },
            {
                "type": "body",
                "duration": 50,
                "narration": "Every flower starts as a tiny seed. The seed is very small, but it has everything it needs to grow into a beautiful flower. When we plant the seed in the soil, something magical begins to happen!",
                "image_description": "Close-up of a small seed in dark, rich soil with tiny roots beginning to emerge"
            },
            {
                "type": "body",
                "duration": 50,
                "narration": "The seed needs three important things to grow. First, it needs water to drink. Second, it needs sunlight to give it energy. And third, it needs good soil with nutrients, which is like food for the plant!",
                "image_description": "A young seedling with water droplets, sunbeams shining down, and healthy dark soil around the roots"
            },
            {
                "type": "body",
                "duration": 50,
                "narration": "As the days pass, the seed sends roots down into the soil to drink water. Then a small green shoot pushes up through the soil. This shoot grows taller and taller, reaching for the sun. Soon, leaves appear on the stem!",
                "image_description": "A growing plant stem with green leaves emerging, roots visible underground, reaching toward a bright sun"
            },
            {
                "type": "body",
                "duration": 40,
                "narration": "Finally, after some time, a bud appears at the top of the stem. The bud slowly opens, and wow! A beautiful flower blooms! The flower has colorful petals that attract bees and butterflies. The bees help make more flowers by spreading pollen!",
                "image_description": "A fully bloomed flower with bright petals, with friendly bees and butterflies visiting it"
            },
            {
                "type": "outro",
                "duration": 20,
                "narration": "Now you know how flowers grow! From a tiny seed to a beautiful bloom. Isn't nature amazing? Remember to take care of plants and flowers around you. Thanks for learning with me today! Bye bye!",
                "image_description": "A happy garden scene with many different colorful flowers blooming, with a child watering them"
            }
        ]
    },

    "Learning Colors with Rainbow Animals": {
        "topic": "Learning Colors with Rainbow Animals",
        "total_duration": 240,
        "sections": [
            {
                "type": "intro",
                "duration": 30,
                "narration": "Hello everyone! Today we're going on a colorful adventure! We're going to meet rainbow animals and learn about different colors. Are you ready? Let's go!",
                "image_description": "A vibrant rainbow arcing across a bright sky with fluffy white clouds"
            },
            {
                "type": "body",
                "duration": 35,
                "narration": "First, let's meet a red animal! Here's a bright red cardinal bird. Red is the color of apples, fire trucks, and strawberries. Can you think of other red things?",
                "image_description": "A cheerful red cardinal bird perched on a branch with red apples nearby"
            },
            {
                "type": "body",
                "duration": 35,
                "narration": "Next is orange! Look at this cute orange goldfish swimming in the water. Orange is the color of oranges, pumpkins, and carrots. Orange is a warm and happy color!",
                "image_description": "A friendly orange goldfish swimming with orange pumpkins and carrots floating around"
            },
            {
                "type": "body",
                "duration": 35,
                "narration": "Now let's see yellow! Here's a bright yellow butterfly. Yellow is the color of the sun, bananas, and lemons. Yellow makes us think of sunshine and happiness!",
                "image_description": "A beautiful yellow butterfly with the sun, bananas, and a lemon in the background"
            },
            {
                "type": "body",
                "duration": 35,
                "narration": "Here comes green! This is a friendly green frog. Green is the color of grass, trees, and leaves. Green reminds us of nature and growing things!",
                "image_description": "A cute green frog sitting on a lily pad surrounded by green grass and trees"
            },
            {
                "type": "body",
                "duration": 35,
                "narration": "Look at this beautiful blue bluebird! Blue is the color of the sky and the ocean. Blue is a cool and calm color that makes us feel peaceful!",
                "image_description": "A bright blue bluebird flying in a clear blue sky above a blue ocean"
            },
            {
                "type": "body",
                "duration": 15,
                "narration": "Last but not least, here's a purple butterfly! Purple is the color of grapes and plums. Purple is a royal and magical color!",
                "image_description": "A majestic purple butterfly with purple grapes and plums"
            },
            {
                "type": "outro",
                "duration": 20,
                "narration": "Great job learning all the colors! Red, orange, yellow, green, blue, and purple make a rainbow! Colors make our world beautiful. See you next time, friends!",
                "image_description": "All the colorful animals together under a complete rainbow - red cardinal, orange fish, yellow butterfly, green frog, blue bird, and purple butterfly"
            }
        ]
    },
}

# Test metadata
TEST_METADATA = {
    "How Do Flowers Grow?": {
        "title": "How Do Flowers Grow? 🌻 Fun Science for Kids",
        "description": """Learn how flowers grow from tiny seeds! 🌱

In this fun educational video, kids will discover:
✅ What seeds need to grow
✅ How roots and stems develop
✅ The magic of blooming flowers
✅ How bees help flowers

Perfect for preschool and early elementary children who love nature and science!

Parents: This video teaches basic plant biology in a simple, engaging way for ages 4-8.

#KidsScience #HowFlowersGrow #EducationalVideos #KidsLearning #NatureForKids #ScienceForKids #LearningIsFun #PreschoolEducation""",
        "tags": [
            "kids education",
            "how flowers grow",
            "science for kids",
            "learning videos",
            "plants for kids",
            "nature education",
            "educational videos",
            "kids learning",
            "preschool videos",
            "children science"
        ],
        "category": 27
    },

    "Learning Colors with Rainbow Animals": {
        "title": "Learning Colors with Rainbow Animals 🌈 Fun for Kids",
        "description": """Let's learn colors with cute rainbow animals! 🐦🐠🦋

In this colorful video, kids will learn:
✅ Red with a cardinal bird
✅ Orange with a goldfish
✅ Yellow with a butterfly
✅ Green with a frog
✅ Blue with a bluebird
✅ Purple with a butterfly

Perfect for toddlers and preschoolers learning their colors!

Parents: This video teaches color recognition through friendly animals and everyday objects.

#LearningColors #RainbowColors #KidsEducation #ToddlerLearning #PreschoolColors #ColorfulAnimals #EducationalVideos #KidsLearning""",
        "tags": [
            "learning colors",
            "colors for kids",
            "rainbow animals",
            "toddler learning",
            "preschool education",
            "kids colors",
            "educational videos",
            "color learning",
            "kids animals",
            "rainbow for kids"
        ],
        "category": 27
    }
}


def get_test_topic():
    """Get a random test topic."""
    import random
    return random.choice(TEST_TOPICS)


def get_test_script(topic):
    """
    Get a test script for a topic.

    Args:
        topic: Topic string

    Returns:
        dict: Script data in VideoScript format
    """
    # Return exact match or first available
    if topic in TEST_SCRIPTS:
        return TEST_SCRIPTS[topic]
    else:
        # Return first available script
        return TEST_SCRIPTS[TEST_TOPICS[0]]


def get_test_metadata(topic):
    """
    Get test metadata for a topic.

    Args:
        topic: Topic string

    Returns:
        dict: Metadata dictionary
    """
    if topic in TEST_METADATA:
        return TEST_METADATA[topic]
    else:
        # Return default metadata
        return TEST_METADATA[TEST_TOPICS[0]]
