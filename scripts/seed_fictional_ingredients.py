#!/usr/bin/env python3
"""Seed the database with fictional ingredients across three thematic groups."""

from src.schemas.domain import FictionalIngredient
from src.services.database import init_db, seed_fictional_ingredients

HIGH_FANTASY = [
    FictionalIngredient(
        name="lembas",
        description=(
            "Elven waybread from Lothlórien. Small cakes that sustain a "
            "traveler for days. Light, sweet, and remarkably filling."
        ),
        thematic_group="high_fantasy",
        taste_profile={"sweet": 0.6, "nutty": 0.3, "earthy": 0.1},
        texture="dense, dry cake",
        rarity="rare",
        magical_properties=(
            "Sustains strength and will far beyond normal food. A single "
            "wafer feeds a grown man for a day of hard labor."
        ),
        preparation_notes=(
            "Made with mallorn flour, honey, and a secret elven process. "
            "Wrapped in mallorn leaves to preserve freshness indefinitely."
        ),
        real_world_approximations=[
            {
                "ingredient": "dense whole grain bread + honey",
                "reasoning": (
                    "Nutrient-dense, long shelf life, natural sweetness"
                ),
            },
            {
                "ingredient": "energy bars (oats, dates, nuts)",
                "reasoning": "Compact calories, portable, sustaining",
            },
        ],
    ),
    FictionalIngredient(
        name="miruvor",
        description=(
            "The cordial of Imladris, a clear, fragrant liquor made by the "
            "Elves of Rivendell. Revives strength and heals weariness."
        ),
        thematic_group="high_fantasy",
        taste_profile={
            "sweet": 0.4,
            "floral": 0.3,
            "herbal": 0.2,
            "warming": 0.1,
        },
        texture="thin liquid, slightly viscous",
        rarity="legendary",
        magical_properties=(
            "Restores vitality and heals minor wounds. Warms the body "
            "against extreme cold. Clarifies the mind."
        ),
        preparation_notes=(
            "Distilled from rare mountain flowers and herbs found only in "
            "hidden valleys. Aged in silver vessels."
        ),
        real_world_approximations=[
            {
                "ingredient": "elderflower liqueur + honey + herbal tincture",
                "reasoning": (
                    "Floral sweetness, herbal complexity, warming alcohol"
                ),
            },
            {
                "ingredient": "mead infused with chamomile and mint",
                "reasoning": "Honey base, soothing herbs, gentle alcohol",
            },
        ],
    ),
    FictionalIngredient(
        name="cram",
        description=(
            "Dale-men's waybread. Hard, biscuit-like, keeps indefinitely but "
            "lacks the grace of lembas. Sustains life but not spirit."
        ),
        thematic_group="high_fantasy",
        taste_profile={"salty": 0.3, "bland": 0.5, "grainy": 0.2},
        texture="very hard, dry biscuit",
        rarity="common",
        magical_properties="None. Purely practical sustenance.",
        preparation_notes=(
            "Baked from coarse flour, water, and salt until all moisture "
            "driven off. Can be softened by soaking in water or stew."
        ),
        real_world_approximations=[
            {
                "ingredient": "hardtack (flour, water, salt)",
                "reasoning": (
                    "Historical ship biscuit, nearly indestructible, bland"
                ),
            },
            {
                "ingredient": "dense rye crackers",
                "reasoning": "Hard, long-lasting, grainy texture",
            },
        ],
    ),
    FictionalIngredient(
        name="honey_cakes",
        description=(
            "Beorn's famous honey-cakes. Twice-baked, rich with wild honey, "
            "served to guests at his hall."
        ),
        thematic_group="high_fantasy",
        taste_profile={"sweet": 0.8, "buttery": 0.2},
        texture="crisp exterior, tender crumb",
        rarity="rare",
        magical_properties=(
            "None, but exceptionally nourishing and mood-lifting."
        ),
        preparation_notes=(
            "Made with cream, eggs, wild honey, and fine flour. Baked slowly, "
            "then cooled and baked again for crispness."
        ),
        real_world_approximations=[
            {
                "ingredient": "honey madeleines or financier cakes",
                "reasoning": "Buttery, honey-sweet, delicate crumb",
            },
            {
                "ingredient": "baklava (simplified)",
                "reasoning": "Honey-soaked, layered, rich",
            },
        ],
    ),
    FictionalIngredient(
        name="elven_wine",
        description=(
            "Pale golden wine from the vineyards of Dorwinion, favored by "
            "Thranduil's court. Light, aromatic, potent."
        ),
        thematic_group="high_fantasy",
        taste_profile={
            "fruity": 0.4,
            "floral": 0.3,
            "crisp": 0.2,
            "alcoholic": 0.1,
        },
        texture="thin liquid, slight viscosity",
        rarity="rare",
        magical_properties=(
            "Induces pleasant dreams, enhances musical perception, "
            "does not cause hangover."
        ),
        preparation_notes=(
            "Grapes grown in magically-tended vineyards. Fermented in "
            "crystal vessels under starlight."
        ),
        real_world_approximations=[
            {
                "ingredient": "late harvest Riesling or Gewürztraminer",
                "reasoning": "Aromatic, slightly sweet, floral, lower alcohol",
            },
            {
                "ingredient": "muscat wine + touch of elderflower",
                "reasoning": "Grapey floral notes, ethereal quality",
            },
        ],
    ),
]


SCI_FI = [
    FictionalIngredient(
        name="spice_melange",
        description=(
            "The spice from Arrakis. Cinnamon-colored powder with geriatric "
            "and prescient properties. Most valuable substance in the universe."
        ),
        thematic_group="sci_fi",
        taste_profile={
            "spicy": 0.4,
            "bitter": 0.3,
            "cinnamon": 0.2,
            "metallic": 0.1,
        },
        texture="fine powder",
        rarity="legendary",
        magical_properties=(
            "Extends life, enhances mental capacity, enables prescience in "
            "high doses. Addictive. Blue eyes (Eyes of Ibad) with "
            "prolonged use."
        ),
        preparation_notes=(
            "Harvested from sandworm excretions on Arrakis. Must be processed "
            "carefully - volatile when exposed to certain conditions. Used "
            "in trace amounts."
        ),
        real_world_approximations=[
            {
                "ingredient": "saffron + cinnamon + pinch of cayenne",
                "reasoning": (
                    "Color, exotic spice notes, mild psychoactive warmth"
                ),
            },
            {
                "ingredient": "turmeric + black pepper + cardamom",
                "reasoning": (
                    "Earthy base, bioavailable compounds, complex flavor"
                ),
            },
        ],
    ),
    FictionalIngredient(
        name="romulan_ale",
        description=(
            "Illegal blue alcoholic beverage in the Federation. Bright blue, "
            "potent, causes severe hangovers. Smuggled across the Neutral Zone."
        ),
        thematic_group="sci_fi",
        taste_profile={
            "sweet": 0.3,
            "sharp": 0.4,
            "metallic": 0.2,
            "burning": 0.1,
        },
        texture="thin liquid, effervescent",
        rarity="rare",
        magical_properties=(
            "Extremely high alcohol content. Causes intense intoxication and "
            "legendary hangovers. Blue color from unknown compound."
        ),
        preparation_notes=(
            "Fermented from Romulan grains using proprietary yeast strains. "
            "Aged in irradiated casks. Contraband in Federation space."
        ),
        real_world_approximations=[
            {
                "ingredient": "blue curaçao + high-proof vodka + lime",
                "reasoning": (
                    "Blue color, sharp alcohol bite, citrus cuts sweetness"
                ),
            },
            {
                "ingredient": "absinthe + butterfly pea flower tea",
                "reasoning": "Herbal complexity, color-changing, high proof",
            },
        ],
    ),
    FictionalIngredient(
        name="synthehol",
        description=(
            "Starfleet's alcohol substitute. Tastes like alcohol but effects "
            "dismissed by conscious choice. No intoxication, no hangover."
        ),
        thematic_group="sci_fi",
        taste_profile={"alcoholic": 0.5, "neutral": 0.5},
        texture="liquid, varies by simulation",
        rarity="common",
        magical_properties=(
            "Simulates alcohol taste and mouthfeel without cognitive "
            "impairment. Effects can be 'turned off' by mental effort."
        ),
        preparation_notes=(
            "Synthesized from molecular templates. Programmed into "
            "replicators. Varieties simulate whisky, wine, beer, etc."
        ),
        real_world_approximations=[
            {
                "ingredient": (
                    "non-alcoholic spirit (Seedlip, Ritual) + bitters"
                ),
                "reasoning": (
                    "Botanical complexity, mouthfeel of alcohol without ethanol"
                ),
            },
            {
                "ingredient": "dealcoholized wine + glycerol",
                "reasoning": "Wine character, body simulation, zero alcohol",
            },
        ],
    ),
    FictionalIngredient(
        name="gagh",
        description=(
            "Klingon delicacy. Live serpent worms served wriggling. "
            "Considered. Eaten raw for maximum freshness. Warrior food."
        ),
        thematic_group="sci_fi",
        taste_profile={
            "umami": 0.5,
            "metallic": 0.2,
            "bitter": 0.2,
            "live": 0.1,
        },
        texture="live, wriggling worms",
        rarity="rare",
        magical_properties=(
            "None. Cultural significance: demonstrates warrior's courage "
            "and stomach."
        ),
        preparation_notes=(
            "Served immediately after harvest. Must be swallowed whole while "
            "still moving. Often accompanied by bloodwine."
        ),
        real_world_approximations=[
            {
                "ingredient": "live octopus (san-nakji) or fermented fish",
                "reasoning": (
                    "Living texture, intense umami, cultural courage food"
                ),
            },
            {
                "ingredient": "spicy ramen with raw egg + squid",
                "reasoning": "Slippery texture, rich umami, interactive eating",
            },
        ],
    ),
    FictionalIngredient(
        name="blue_milk",
        description=(
            "Tatooine staple. Blue-colored milk from female banthas. Sweet, "
            "rich, served cold. Iconic breakfast drink."
        ),
        thematic_group="sci_fi",
        taste_profile={
            "sweet": 0.5,
            "creamy": 0.3,
            "vanilla": 0.1,
            "nutty": 0.1,
        },
        texture="thick, creamy liquid",
        rarity="common",
        magical_properties="None. Nutrient-rich desert sustenance.",
        preparation_notes=(
            "Harvested from domesticated banthas. Naturally blue from unique "
            "proteins. Best served chilled."
        ),
        real_world_approximations=[
            {
                "ingredient": "whole milk + blue spirulina + honey + vanilla",
                "reasoning": "Natural blue color, creamy, sweet, nutritious",
            },
            {
                "ingredient": "coconut milk + butterfly pea powder + maple",
                "reasoning": "Plant-based, color-changing, rich",
            },
        ],
    ),
]


MYTHOLOGICAL = [
    FictionalIngredient(
        name="ambrosia",
        description=(
            "Food of the Greek gods. Conferred immortality. Described as "
            "sweet, fragrant, brought by doves to Olympus."
        ),
        thematic_group="mythological",
        taste_profile={"sweet": 0.7, "honey": 0.2, "divine": 0.1},
        texture="varies (fruit, honey, nectar-like)",
        rarity="legendary",
        magical_properties=(
            "Grants immortality and eternal youth to gods. Mortals who "
            "consume become divine or die. Heals all wounds."
        ),
        preparation_notes=(
            "Prepared by Hebe or Ganymede. Served at heavenly feasts. "
            "Cannot be replicated by mortal means."
        ),
        real_world_approximations=[
            {
                "ingredient": "honeycomb + fresh figs + orange blossom water",
                "reasoning": (
                    "Divine sweetness, ancient associations, floral perfume"
                ),
            },
            {
                "ingredient": (
                    "ambrosia salad (coconut, orange, marshmallow, sour cream)"
                ),
                "reasoning": "Classic 'ambrosia' dessert, sweet and rich",
            },
        ],
    ),
    FictionalIngredient(
        name="nectar",
        description=(
            "Drink of the Greek gods. Often paired with ambrosia. Sweet, "
            "intoxicating, the 'wine of the gods'."
        ),
        thematic_group="mythological",
        taste_profile={"sweet": 0.6, "floral": 0.2, "wine": 0.2},
        texture="thick, syrupy liquid",
        rarity="legendary",
        magical_properties=(
            "Confers immortality with ambrosia. Intoxicating to gods. "
            "Mortals driven mad or killed by taste."
        ),
        preparation_notes=(
            "Pressed from divine grapes or distilled from flowers of Olympus. "
            "Served in golden cups."
        ),
        real_world_approximations=[
            {
                "ingredient": "late harvest dessert wine + honey + rose water",
                "reasoning": "Lush sweetness, floral divinity, golden color",
            },
            {
                "ingredient": "mead + hibiscus + pomegranate molasses",
                "reasoning": "Ancient drink, ruby color, complex sweetness",
            },
        ],
    ),
    FictionalIngredient(
        name="soma",
        description=(
            "Vedic ritual drink. Pressed from a mysterious mountain plant. "
            "Grants divine vision, strength, and poetic inspiration."
        ),
        thematic_group="mythological",
        taste_profile={
            "bitter": 0.4,
            "astringent": 0.3,
            "herbal": 0.2,
            "sweet": 0.1,
        },
        texture="thin, frothy liquid",
        rarity="legendary",
        magical_properties=(
            "Induces ecstatic states, divine communion, enhanced strength "
            "and poetic power. 'We have drunk Soma, we have become immortal.'"
        ),
        preparation_notes=(
            "Plant stalks pounded between stones, filtered through wool, "
            "mixed with milk and water. Consumed fresh in fire rituals."
        ),
        real_world_approximations=[
            {
                "ingredient": "ephedra tea + milk + honey (historical theory)",
                "reasoning": "Stimulant plant, ritual preparation, milk base",
            },
            {
                "ingredient": "kava + coconut water + lime",
                "reasoning": (
                    "Psychoactive root, ceremonial use, earthy bitterness"
                ),
            },
        ],
    ),
    FictionalIngredient(
        name="golden_apples",
        description=(
            "Apples of the Hesperides (Greek) / Idunn (Norse). Golden, "
            "glowing, grant eternal youth. Guarded by dragons/giants."
        ),
        thematic_group="mythological",
        taste_profile={"sweet": 0.5, "tart": 0.2, "honey": 0.2, "divine": 0.1},
        texture="crisp, juicy apple",
        rarity="legendary",
        magical_properties=(
            "Grants eternal youth and immortality. In Norse myth, gods age "
            "without them. Heracles and Thor sought them."
        ),
        preparation_notes=(
            "Grow on sacred trees in far gardens. Must be plucked at perfect "
            "ripeness. Do not rot."
        ),
        real_world_approximations=[
            {
                "ingredient": (
                    "golden delicious + honey drizzle + edible gold leaf"
                ),
                "reasoning": "Golden color, honey sweetness, visual splendor",
            },
            {
                "ingredient": "quince paste (membrillo) + apple jelly",
                "reasoning": "Ancient fruit, golden, intense flavor, preserves",
            },
        ],
    ),
    FictionalIngredient(
        name="mead_of_poetry",
        description=(
            "Norse mead brewed from Kvasir's blood (wisest being) mixed with "
            "honey. Grants poetic inspiration and wisdom."
        ),
        thematic_group="mythological",
        taste_profile={
            "honey": 0.4,
            "fermented": 0.3,
            "complex": 0.2,
            "metallic": 0.1,
        },
        texture="thick, amber liquid",
        rarity="legendary",
        magical_properties=(
            "Anyone who drinks becomes a skald (poet) with perfect verse "
            "and wisdom. Stolen by Odin in eagle form."
        ),
        preparation_notes=(
            "Blood of Kvasir fermented with honey in three vats (Óðrerir, "
            "Boðn, Són). Hidden in mountain."
        ),
        real_world_approximations=[
            {
                "ingredient": "traditional mead + blood orange + spices",
                "reasoning": "Honey base, deep color, complex fermentation",
            },
            {
                "ingredient": "braggot (mead + malt) + herbs",
                "reasoning": (
                    "Ancient hybrid, herbal complexity, poetic heritage"
                ),
            },
        ],
    ),
]


ALL_INGREDIENTS = HIGH_FANTASY + SCI_FI + MYTHOLOGICAL


if __name__ == "__main__":
    init_db()
    count = seed_fictional_ingredients(ALL_INGREDIENTS)
    print(f"Seeded {count} fictional ingredients")
