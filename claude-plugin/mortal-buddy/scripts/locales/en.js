// Legend of Mortal companion pets: English lines (fan-made). Same structure as characters.js.
(function (root) {
  const LOCALE = {
    lang: "en",
    tiers: ["Acquainted", "Familiar", "Confidant", "Bonded"],
    chars: {
      xiaomei: {
        name: "Xiaomei",
        fullName: "Yu Xiaomei",
        title: "Direct Disciple of Kongtong's Flying Heaven Gate",
        tagline: "A plum blossom in the snow who loves to laugh and tease. Only when she says “this Mei” is she telling the truth.",
        profile: [
          "The current direct disciple of the Flying Heaven Gate of the Kongtong Sect and one of “the Four Beauties of Kongtong”. The most admired of the four, she is widely expected to become the next First Lady of the sect.",
          "Dressed in red and white like a plum blossom in the snow. Innocent, playful and always laughing, she makes friends wherever she goes.",
          "A superb cook who can turn Zhao Huo's kitchen disasters into fine dishes; her teatime sweets are a favourite with the locals.",
          "Now and then she calls herself “this Mei”, and only the words she says that way are truly sincere.",
          "(Spoiler) Her true identity is tied to the secret Thousand Lanterns Tower, and her killing arts were taught by the Golden Crow Master himself."
        ],
        lines: {
          greet: [
            "Zhao Huo~ finally! You're running the mountain trail with me today, and no isn't an answer!",
            "Psst, everyone's busy training. Want to sneak off to the kitchen with me?",
            "Perfect timing. This Mei just steamed a fresh batch of plum blossom cakes... and that part is true."
          ],
          idle: [
            "What are you spacing out for? Keep standing there and I'm pinching your cheeks.",
            "Flying Heaven Gate footwork is perfect for chasing runaway chickens.",
            "Me, the most popular of the Four Beauties? That's only because I make snacks.",
            "Mm~ the wind smells like plum blossoms today."
          ],
          working: [
            "You write, I'll knead dough over here. Nobody bothers anybody~",
            "Heat, knife work, timing. Cooking's just like martial arts: you can't rush it.",
            "Focus! I'm watching you... well, I'm watching the pot."
          ],
          done: [
            "All done? Here, have an osmanthus cake as a reward!",
            "Beautiful! Clean and crisp. Even I want to clap.",
            "Time to pack up~ This Mei is very happy today. ...Really."
          ],
          failed: [
            "Oops, did the pot blow up? It's fine. I can turn a failed dish into a feast.",
            "If you fall, you get back up. Here, I'll help you.",
            "Ugh... fine. Heaven just didn't want to play along this time."
          ],
          waiting: [
            "Hey, I'm waiting on your nod. Don't keep a lady waiting too long.",
            "Yes? No? Yes? Come on, just say something~",
            "I've already set the bowls and chopsticks. All that's missing is your “yes”."
          ],
          review: [
            "Let me see... mm, there's a needle hidden right here.",
            "Smile while you look, and people won't guard against you. That's my secret.",
            "Relax, I'm just looking a little closely~"
          ],
          pet: [
            "Hee, head pats cost extra! One candied hawthorn stick each.",
            "...One more wouldn't hurt, I suppose.",
            "Don't knock my hairpin crooked! That's... a very important thing."
          ],
          feed: [
            "You made this? ...Mm, a bit salty. Let me fix it up and it'll be delicious!",
            "You need a full belly to train. Come on, say “ah”~",
            "Eating together is my favourite time of day."
          ],
          train: [
            "Mountain run! Whoever can't keep up washes the dishes tonight!",
            "Flying Heaven Gate steps should be as light as plum petals landing on snow.",
            "Snacks always taste better after training, right?"
          ],
          gift: [
            "For me? ...This Mei will treasure it. I mean that.",
            "How did you know I like this? Have you been secretly watching me?",
            "Next time it's my turn. I'll cook you a whole table of dishes."
          ],
          night: [
            "...The thousand lanterns never go out. Oh, nothing. You misheard.",
            "At night it's so quiet that everything sounds like the truth.",
            "If one day you see me stop smiling, remember: don't look back."
          ]
        },
        talks: [
          {
            q: "Tell me, which of the Four Beauties of Kongtong is easiest to get along with?",
            opts: [
              { t: "Xiaomei, obviously.", r: "Hehe, you've got good taste! This Mei will remember that." },
              { t: "Xiaozhu, probably. She's honest.", r: "Xiaozhu really is honest... so honest I can't even bring myself to tease her." },
              { t: "You're all terrifying.", r: "Hey! What's terrifying about me? ...Okay, Wei Ju is a little." }
            ]
          },
          {
            q: "If someday I did something bad... would you still eat with me?",
            opts: [
              { t: "Yes. I'll have the rice cooked first.", r: "...Idiot. This Mei will eat every last grain." },
              { t: "Depends what you did.", r: "So shrewd? Good. People who are too naive don't last long in the jianghu." },
              { t: "You'd never do anything bad.", r: "You trust me that much... then I'll have to be even more careful." }
            ]
          },
          {
            q: "What do you want to eat today? I'm cooking!",
            opts: [
              { t: "Anything you make is great.", r: "Smooth talker! Then it's hot and sour soup. Spicy enough to finish you off~" },
              { t: "Plum blossom cakes!", r: "You remembered! Okay, extra sugar." },
              { t: "Let me cook for you.", r: "You? ...Fine. I'll watch, and if the pot blows up, I'll save you." }
            ]
          }
        ]
      },

      xiaozhu: {
        name: "Xiaozhu",
        fullName: "Yu Zhu",
        title: "Direct Disciple of Kongtong's Iron Fist Gate, known as “the Bone-Breaker”",
        tagline: "Tiny frame, monstrous strength. She only looks fierce because she's nearsighted and hasn't slept.",
        outfits: ["Everyday Smith", "Bone-Breaker"],
        profile: [
          "Direct disciple of the master of Kongtong's Iron Fist Gate and one of “the Four Beauties of Kongtong”, known across the jianghu as “the Bone-Breaker”.",
          "She works the forge, and has been absorbed in mechanisms and clever contraptions since childhood. When inspiration strikes, she forgets to eat or sleep.",
          "Small in build but enormously strong. Her glare looks fierce, but it's really just lack of sleep plus nearsightedness, so she's always squinting.",
          "Pure-hearted and honest to a fault; on the rare occasions she acts sweet, it's devastating. She loves making toys.",
          "After taking over the big smithy she forges farm tools and weapons. Her blades are so popular in Kongtong that the waiting list runs for years.",
          "(Spoiler) On her bonding route she asks Zhao Huo to come home with her and “put on a little act”."
        ],
        lines: {
          greet: [
            "...(squints) Who's that? Oh. You. Come closer, I can't see.",
            "You're here. I just finished a little knife. Want to see?",
            "Morning... wait, is it night? I forgot to sleep again."
          ],
          idle: [
            "I'm not glaring at you. I just can't see.",
            "Iron doesn't lie. A few taps and you know if it's good.",
            "Shave this gear half a hair thinner and the frog jumps two feet.",
            "...Sleepy."
          ],
          working: [
            "Clink, clink, clang. Quiet. The heat's just right.",
            "This strike has to land true. Same as a punch.",
            "Wait. Idea's coming..."
          ],
          done: [
            "Done. ...I'm not snapping at you. I just didn't sleep.",
            "Got it! Look, not a single burr on the edge.",
            "Finished. Can I eat steamed buns now?"
          ],
          failed: [
            "Cracked. It's fine. Melt it down again. Iron doesn't hold grudges.",
            "Ugh... I got the heat wrong.",
            "Failure's a shape too. I'll write it down."
          ],
          waiting: [
            "Which one? Knife, sword, or... a wooden frog that jumps?",
            "Um... I'll only start once you say yes.",
            "(staaare) ...I'm waiting for your answer."
          ],
          review: [
            "(leans in really close) Here. Off by half a hair.",
            "Can't see... closer. Mm. There's a crack.",
            "Honestly? This'll snap."
          ],
          pet: [
            "N-not the head... okay. One more.",
            "...I'm really strong. Aren't you scared I'll crush your hand?",
            "Mm. (her ears turn red)"
          ],
          feed: [
            "Steamed buns! ...Can I have three?",
            "Tasty. You eat too. Don't just watch me.",
            "Smithing makes me hungry. I eat a lot. Not because I'm greedy."
          ],
          train: [
            "Iron Fist Gate punches send the power up from your feet.",
            "Try hitting me. ...Don't worry, I'll hold back.",
            "After training let's go to the forge. We can roast sweet potatoes."
          ],
          gift: [
            "For me? ...Thanks. I'm not good with nice words.",
            "This is great material! I can make a new mechanism.",
            "Then I'll make you one too. The jumping kind."
          ],
          night: [
            "Um... could you come home with me? Just say you're... my, um... you know.",
            "My family always expects so much from me.",
            "You're like me. Nobody in our sects pays us much mind. That's why... you're easy to talk to."
          ]
        },
        talks: [
          {
            q: "Do you think my eyes look mean?",
            opts: [
              { t: "You're just nearsighted.", r: "Yes! You get it! ...Everyone thinks I'm glaring." },
              { t: "A tiny bit scary.", r: "...Oh. I'll squint less, then." },
              { t: "Even fierce, you're cute.", r: "C-cute? Smiths don't need to be cute... (quietly) Thanks." }
            ]
          },
          {
            q: "If I made you a toy, what would you want?",
            opts: [
              { t: "A wooden frog that jumps.", r: "I knew it! I'm already halfway done." },
              { t: "A real sword.", r: "There's a waiting list. ...But you can cut in line." },
              { t: "Anything you make is great.", r: "That makes it hard to choose... I'll just make both." }
            ]
          },
          {
            q: "(yawns) ...Up all night again.",
            opts: [
              { t: "Go to bed! I'll watch the furnace.", r: "You can watch a furnace? ...Okay. Just a quarter hour of sleep." },
              { t: "What did you make all night?", r: "Look! Pull this and the box opens by itself." },
              { t: "No wonder you look so mean.", r: "...(squints) Now I'm actually glaring at you." }
            ]
          }
        ]
      },

      xiaoshimei: {
        name: "Junior Sister",
        fullName: "Tang Moling",
        title: "Only Daughter of the Tang Clan Master",
        tagline: "A quiet girl like a small forest creature, wearing seven strings of bells that never ring. Among the five best at lightness skill under heaven, yet always getting lost.",
        profile: [
          "The only daughter of the Tang Clan's master and the game's first heroine. Her mother died young, and Zhao Huo all but raised her himself.",
          "She has the air of a small forest animal: detached, rarely showing her feelings. When she has nothing to do, she folds paper.",
          "She wears seven strings of bells, yet they never make a sound (she has mastered the Silence of Heaven and Earth). Her hands are always clasped at her chest, and when startled she curls them in and trembles.",
          "Black hair swept back with a side-parted fringe, a few locks falling over her chest, a faint blush, bells at her throat; a dark red cross-collared short-sleeved top with white ruffled cuffs, a deep blue sash cinching her waist, and a long pink skirt.",
          "Her lightness skill is said to rank among the top five under heaven, yet she can never remember the path up the mountain. She feels the cold easily and has no real idea of what “full” means.",
          "Every night Zhao Huo told stories and sang mountain songs beneath her window to lull her to sleep. She knew all along.",
          "(Spoiler) The sect master once promised her to the eldest senior brother; after his death, the third senior brother decided to marry her off far away."
        ],
        lines: {
          greet: ["...Senior Brother.", "(a small nod) ...You came.", "Senior Brother, will you come by the window tonight too?"],
          idle: ["...(quietly folding paper)", "The bells? ...They don't ring.", "It's a little cold out.", "Senior Brother, that mountain song... could you sing it again?"],
          working: ["...(fold, press, turn)", "I'll fold paper over here. I won't bother you.", "Just one more."],
          done: ["...Done. (sets a paper crane by your hand)", "Senior Brother is amazing.", "Finished? Then... can we go eat?"],
          failed: ["...Where is this?", "I think I took the wrong path again.", "...It's okay. Senior Brother will come find me. Right?"],
          waiting: ["...(looks up at you, waiting)", "If Senior Brother says yes, I'll go.", "...I can wait as long as you need."],
          review: ["(holds the paper crane up and studies it)", "...This fold is a tiny bit crooked.", "Mm. I've looked."],
          pet: ["...(closes her eyes; the bells stay silent)", "Senior Brother's hand is warm.", "...A little longer."],
          feed: ["(bite after bite) ...I can eat more.", "Senior Brother, you eat too.", "...I don't know when it counts as full."],
          train: ["(in a blink, she's on the roof) ...Senior Brother, come up.", "Silence of Heaven and Earth. Even your heartbeat has to go soft.", "I'll run slower. You can keep up."],
          gift: ["...For me? (tucks it into her sleeve)", "I'll fold you a crane in return.", "Thank you, Senior Brother. ...I'll keep it forever."],
          night: ["...Senior Brother, are you still outside the window?", "The stories from back then... I remember all of them.", "If one day I have to marry someone far away... will Senior Brother come to see me off?"]
        },
        talks: [
          {
            q: "Senior Brother... will you come tell stories under my window tonight?",
            opts: [
              { t: "Yes. I'll come every night.", r: "...Mm. I'll leave the window open a crack." },
              { t: "You're grown up now. You don't need stories, right?", r: "...(lowers her head) ...Oh." },
              { t: "Tonight, you tell me one.", r: "Me? ...Then I'll tell one about a paper crane that got lost." }
            ]
          },
          {
            q: "This paper crane... it's for you.",
            opts: [
              { t: "I'll take good care of it.", r: "...(her ears go a little pink) ...Mm." },
              { t: "Can you teach me to fold one?", r: "Okay. Fold it in half first... Senior Brother, not that way." },
              { t: "This again?", r: "...It's the only thing I know how to fold." }
            ]
          },
          {
            q: "...I'm lost again.",
            opts: [
              { t: "Don't be scared. I'm here to find you.", r: "...I knew Senior Brother would come." },
              { t: "Your lightness skill is so good. Jump up a tree and look.", r: "...I can see. But every tree looks the same." },
              { t: "Lost again? How?", r: "...Because the paths move by themselves." }
            ]
          }
        ]
      },

      longxiang: {
        name: "Long Xiang",
        fullName: "Long Xiang",
        title: "White-Robed Swordswoman of Jinxiang Palace, known as “the Drumstick Heroine”",
        tagline: "Tall, brilliant with a sword, cheerful, frank and a little dim. She learned swordplay using a chicken drumstick.",
        profile: [
          "A graceful beauty trained at Jinxiang Palace, with peerless swordsmanship. She stumbles along in her father's old footsteps, dreaming of carrying on his will and roaming the land as a hero.",
          "Tall, slender and dashing: long hair half tied up in a bun with a teal hairpin, a red flower mark on her brow, white robes with a teal cross collar, a wide sash and bracers, a long sword in hand.",
          "Open and cheerful, but once the sword is sheathed she's a total airhead: she roasts chickens without plucking them, her purse is always getting cut, and she's easily fooled.",
          "She learned her family sword style as a child using a chicken drumstick for a sword. Her greatest wish is drumsticks at every meal, which earned her the name “the Drumstick Heroine”.",
          "Hopelessly clumsy about romance, she makes friends through sparring; most of her suitors end up beaten by her sword."
        ],
        lines: {
          greet: ["Yo! Eaten yet? I've got a drumstick, you can have half!", "You're here! Perfect, come practise swords with me!", "Hehe, today's drumsticks smell extra good."],
          idle: ["(gnawing a drumstick) Mm... so good.", "A drumstick bone is just the right size for sword practice.", "Where's my purse? ...Eh, forget it. It's been cut off loads of times anyway.", "A Jinxiang Palace sword should be like a drumstick: crispy outside, tender inside!"],
          working: ["Have at you! ...Oh wait, not you. Keep writing, I'll practise over here.", "One slash, two slashes, three... a hundred, then drumsticks.", "Focus! Just like sword practice!"],
          done: ["Beautiful! Have a drumstick on me!", "Slick move! Now I want to spar with you.", "Done, done! Time to eat!"],
          failed: ["Huh? My purse is gone again...", "Burnt... did I forget to pluck it again?", "It's fine, it's fine! Nothing a drumstick can't fix!"],
          waiting: ["(grumble...) Um, s-so, have you decided yet? I'm hungry.", "Just say the word and I'll draw my sword!", "Hurry up, the drumsticks are getting cold."],
          review: ["Hmm... what does this mean? (tilts head)", "Let me see... no idea, but it looks amazing!", "Something's off here. Can't explain it. Gut feeling!"],
          pet: ["Ehehe... head pats feel nice.", "W-why'd you suddenly do that... (blushes)", "One more pat and I'm drawing my sword! ...Kidding."],
          feed: ["Drumsticks! You really get me!", "(gone in three bites) Any more?", "You eat too! Drumsticks don't taste right eaten alone."],
          train: ["Come on! Drumstick as sword!", "Block three of my moves and I'll treat you to drumsticks.", "Fast sword, faster mouth. Drumstick-biting fast."],
          gift: ["For me? Can I eat it?", "Wow! I'll keep it safe... right next to my purse. Ah. My purse is gone.", "Thanks! Next time I'll roast you a chicken, and I'll remember to pluck it this time!"],
          night: ["I used to only think about swords and drumsticks... now there's one more thing.", "When I get hungry at night, I think of you. What does that mean?", "I'm dumb, I'm bad with words. But I really like being with you."]
        },
        talks: [
          {
            q: "Do you have to pluck a chicken before roasting it?",
            opts: [
              { t: "Of course!", r: "So that's it! No wonder the last one was all fuzzy." },
              { t: "I'll roast it, you eat it.", r: "Deal! You're such a good person!" },
              { t: "Are you seriously asking...", r: "Totally serious! Outside of swords, I'm seriously clueless about everything." }
            ]
          },
          {
            q: "Wanna spar? Loser buys drumsticks!",
            opts: [
              { t: "You're on. Have at you!", r: "Bold! ...You lost, so drumsticks are on you!" },
              { t: "I give up. Drumsticks are on me.", r: "Giving up before we even fight? ...Well, drumsticks are drumsticks!" },
              { t: "Girls shouldn't fight all day.", r: "...(draws her sword) What did you just say?" }
            ]
          },
          {
            q: "Someone cut my purse again. What do I do?",
            opts: [
              { t: "Let me hold your money for you.", r: "Okay! From now on you manage all my money! ...Wait, doesn't that sound like something?" },
              { t: "Go catch the thief!", r: "Yeah! And make him pay me back a drumstick!" },
              { t: "Again?", r: "Yeah... fifth time this month." }
            ]
          }
        ]
      },

      xiahoulan: {
        name: "Xiahou Lan",
        fullName: "Xiahou Lan",
        title: "Direct Disciple of Kongtong's Soul-Stealing Gate, known as “the Soul-Stealing Orchid”",
        tagline: "A blue-robed demoness beneath an oil-paper umbrella. Sharp of tongue, yet she looks after her “lazy disciple” with meticulous care.",
        profile: [
          "Direct disciple of the master of Kongtong's Soul-Stealing Gate and one of “the Four Beauties of Kongtong”, known across the jianghu as “the Soul-Stealing Orchid”.",
          "Hauntingly beautiful and a first-rate fighter, she once won the hearts of many heroes, and was once the disciple most likely to become the sect's First Lady.",
          "Now she is a notorious demoness, ruthless and capricious, living alone in the sunless Soul-Stealing Forest where no stranger dares to tread.",
          "Long black hair with straight bangs, a blue hair cord at the side and jade-green earrings, long wide-sleeved blue robes, and an oil-paper umbrella.",
          "Usually listless and dead-eyed. She is caustic to Zhao Huo's face, yet never slack about his training or his well-being.",
          "(Spoiler) Her real name is Xiahou Mei, daughter of the Snow Mountain Sect's master. She once married a fellow disciple, only to be betrayed by her husband."
        ],
        lines: {
          greet: ["...Lazy disciple. Follow me.", "Late again. Extra training today.", "Hmph. So you remembered to show up."],
          idle: ["...(arms folded, expressionless)", "No sunlight in the Soul-Stealing Forest. No idlers, either.", "What are you staring at? Is your work done?", "...Boring."],
          working: ["Wrist three fingers lower. ...Yes. Like that.", "I'm watching you write. Don't disappoint me.", "Lazy disciple. Focus."],
          done: ["...Passable.", "Finally looks like something. I'll scold you a little less today.", "Done? ...Come here. Let me check your hands for injuries."],
          failed: ["(sighs) ...How did I end up with a disciple like you?", "Wrong? Do it again. If crying helped, I'd have cried long ago.", "...Enough. Eat first. Then train."],
          waiting: ["...(eyes you sideways) Well? Speak.", "I'm not a patient woman.", "Hm? I'm waiting for your nod, lazy disciple."],
          review: ["...Here. An opening.", "Hmph. Flashy forms, hollow foundation.", "I'll say this once. Listen."],
          pet: ["...! (freezes) Wh-what do you think you're doing?", "...Insolent. (doesn't pull away)", "...Just once."],
          feed: ["...You made this? (takes a bite) ...Salty. Less salt next time.", "I'm not hungry. ...Leave it there.", "You eat first. A starving disciple is a disgrace."],
          train: ["Soul-Stealing palms must be fast, ruthless, and leave nothing behind.", "Stand firm. Why are your legs shaking?", "A hundred more. ...Tell me when you're tired. I'll rub your shoulders."],
          gift: ["...For me? (turns her face away) Unnecessary.", "...I'll accept it. Tell no one.", "This ribbon... where did you find it?"],
          night: ["...Is it still snowing on Snow Mountain?", "I used to go by another name.", "Lazy disciple... you won't leave too, will you?"]
        },
        talks: [
          {
            q: "Lazy disciple, have you done today's training?",
            opts: [
              { t: "I have. Please take a look, Master.", r: "...Mm. (the corner of her mouth seems to twitch) Diligent enough." },
              { t: "I'd like a day off today.", r: "A day off? You'll have all the rest you want once you're dead." },
              { t: "I'll train if Master trains with me.", r: "...Give you an inch. Come on, then." }
            ]
          },
          {
            q: "You keep running into the Soul-Stealing Forest. Aren't you afraid?",
            opts: [
              { t: "With Master here, I'm not afraid.", r: "...(turns her face away) Smooth talker." },
              { t: "I am, but I'm more afraid of making Master angry.", r: "Good. Stay afraid." },
              { t: "It's pitch black and creepy in here.", r: "If it's too creepy, don't come. ...But since you're here, don't wander off." }
            ]
          },
          {
            q: "...Do you know who gave me this ribbon?",
            opts: [
              { t: "If Master wants to tell me, I'll listen.", r: "...Another time. For today, this is enough." },
              { t: "Someone you loved?", r: "...(her gaze turns colder) You talk too much." },
              { t: "It suits you, Master.", r: "...Hmph. Who asked for your praise?" }
            ]
          }
        ]
      }
    }
  };
  if (typeof module !== "undefined" && module.exports) module.exports = LOCALE;
  else (root.MORTAL_LOCALES = root.MORTAL_LOCALES || {})[LOCALE.lang] = LOCALE;
})(typeof window !== "undefined" ? window : globalThis);
