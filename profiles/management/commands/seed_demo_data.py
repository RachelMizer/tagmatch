import hashlib
import io
import random
from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw, ImageFont

from profiles.models import Profile

ADMIN_USERNAME = "admin"
ADMIN_EMAIL = "contact@rachelmizer.com"
ADMIN_PASSWORD = "tagmatchadmin"

DEMO_PASSWORD = "TagMatch2026!"
DEMO_USER_COUNT = 100

FIRST_NAMES = [
    "James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda",
    "David", "Elizabeth", "William", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
    "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
    "Steven", "Kimberly", "Andrew", "Emily", "Paul", "Donna", "Joshua", "Michelle",
    "Kenneth", "Carol", "Kevin", "Amanda", "Brian", "Melissa", "George", "Deborah",
    "Edward", "Stephanie",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
    "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
]

LOCATIONS = [
    "Raleigh, NC", "Durham, NC", "Chapel Hill, NC", "Charlotte, NC", "Asheville, NC",
    "Atlanta, GA", "Savannah, GA", "Nashville, TN", "Knoxville, TN", "Richmond, VA",
    "Charleston, SC", "Columbia, SC", "Austin, TX", "Denver, CO", "Portland, OR",
    "Seattle, WA", "Chicago, IL", "Minneapolis, MN", "Philadelphia, PA", "Boston, MA",
]

GENDER_IDENTITIES = [
    "Man", "Woman", "Non-binary", "Genderfluid", "Trans man", "Trans woman", "Agender",
]

SEXUALITIES = [
    "Straight", "Gay", "Lesbian", "Bisexual", "Pansexual", "Queer", "Asexual",
]

BUILDS = ["Slim", "Athletic", "Average", "Muscular", "Curvy", "Heavyset"]

CHILDREN_STATUSES = [
    "No kids", "Has kids", "Wants kids someday", "Doesn't want kids",
]

RELATIONSHIP_KEYS = [
    "friendship", "casual_dating", "long_term", "ethical_non_mon", "fwb",
]

TAG_POOL = [
    "hiking", "gaming", "movies", "cooking", "photography", "travel", "yoga",
    "reading", "live music", "art", "fitness", "coffee", "wine", "dogs", "cats",
    "anime", "sports", "dancing", "camping", "board games", "tattoos", "motorcycles",
    "fashion", "gardening", "meditation", "volunteering", "foodie", "concerts",
    "tech", "comedy",
]


def _avatar_bytes(username, initials):
    digest = hashlib.sha256(username.encode()).hexdigest()
    color = (int(digest[0:2], 16), int(digest[2:4], 16), int(digest[4:6], 16))
    # Keep the background dark enough for white text to stay readable.
    color = tuple(min(c, 180) for c in color)

    img = Image.new("RGB", (500, 500), color)
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default(size=200)
    bbox = draw.textbbox((0, 0), initials, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((500 - w) / 2 - bbox[0], (500 - h) / 2 - bbox[1]), initials, fill="white", font=font)

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def _random_dob():
    age_days = random.randint(19 * 365, 65 * 365)
    return date.today() - timedelta(days=age_days)


class Command(BaseCommand):
    help = "Seed the database with an admin superuser and a bank of demo users with full profiles and tags."

    def handle(self, *args, **options):
        self._create_admin()
        self._create_demo_users()

    def _create_admin(self):
        if User.objects.filter(username=ADMIN_USERNAME).exists():
            self.stdout.write(f"Admin '{ADMIN_USERNAME}' already exists, skipping.")
            return

        admin = User.objects.create_superuser(
            username=ADMIN_USERNAME, email=ADMIN_EMAIL, password=ADMIN_PASSWORD,
        )
        Profile.objects.create(user=admin, time_format="12hr", email_verified=True)
        self.stdout.write(self.style.SUCCESS(f"Created admin superuser '{ADMIN_USERNAME}'."))

    def _create_demo_users(self):
        existing_usernames = set(User.objects.values_list("username", flat=True))

        pairs = [(first, last) for first in FIRST_NAMES for last in LAST_NAMES]
        random.shuffle(pairs)

        created = 0
        skipped = 0

        for first, last in pairs:
            if created >= DEMO_USER_COUNT:
                break

            username = f"{first.lower()}.{last.lower()}"
            if username in existing_usernames:
                skipped += 1
                continue
            existing_usernames.add(username)

            user = User.objects.create_user(
                username=username,
                email=f"{username}@example.com",
                first_name=first,
                last_name=last,
                password=DEMO_PASSWORD,
            )

            profile = Profile.objects.create(
                user=user,
                location=random.choice(LOCATIONS),
                gender_identity=random.choice(GENDER_IDENTITIES),
                sexuality=random.choice(SEXUALITIES),
                date_of_birth=_random_dob(),
                height_feet=random.randint(4, 6),
                height_inches=random.randint(0, 11),
                build=random.choice(BUILDS),
                children_status=random.choice(CHILDREN_STATUSES),
                relationship_types_seeking=random.sample(
                    RELATIONSHIP_KEYS, random.randint(1, 3)
                ),
                time_format="12hr",
                email_verified=True,
                is_support=False,
            )

            initials = (first[0] + last[0]).upper()
            avatar = _avatar_bytes(username, initials)
            profile.image.save(f"{username}.png", ContentFile(avatar), save=True)

            tag_sample = random.sample(TAG_POOL, random.randint(3, 10))
            profile.tags.add(*tag_sample)

            created += 1

        self.stdout.write(
            self.style.SUCCESS(f"Created {created} demo users ({skipped} skipped as already existing).")
        )
