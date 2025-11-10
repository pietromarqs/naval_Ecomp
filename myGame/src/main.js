import kaplay from "kaplay";
// import "kaplay/global"; // uncomment if you want to use without the k. prefix

<<<<<<< HEAD
// simple rpg style walk and talk

kaplay({
    background: [500, 500, 82],
});


loadSprite("water", "/sprites/water.png");
loadSprite("barco2", "/sprites/barco 2b.png")


scene("main", (levelIdx) => {


    // level layouts
    const levels = [
        [
            "==========",
            "==========",
            "==========",
            "==========",
            "==========",
            "==========",
            "==========",
            "==========",
            "==========",
            "==========",

        ],

    ];

    const level = addLevel(levels[levelIdx], {
        tileWidth: 64,
        tileHeight: 64,
        pos: vec2(70, 70),
        tiles: {
            "=": () => [
                sprite("water"),
                area(),
                body({ isStatic: true }),
                anchor("center"),
            ],

        },
        // any() is a special function that gets called everytime there's a
        // symbole not defined above and is supposed to return what that symbol
        // means

    });

    // get the player game obj by tag









});

scene("win", () => {
    add([
        text("You Win!"),
        pos(width() / 2, height() / 2),
        anchor("center"),
    ]);
});

go("main", 0);
=======
const k = kaplay();

k.loadRoot("./"); // A good idea for Itch.io publishing later
k.loadSprite("bean", "sprites/bean.png");

k.add([k.pos(120, 80), k.sprite("bean")]);

k.onClick(() => k.addKaboom(k.mousePos()));
>>>>>>> origin/miguel

