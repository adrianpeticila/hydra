/* hydra-lexicon.js — the word lists both heads share.
   Slop Detector reads pasted text with it. Homepage Roaster reads a fetched page with it.
   One copy, so a marker added here shows up in every tool. English only. */

const BANNED = ["synergy","synergies","leverage","leveraging","leveraged","dive into","diving into",
 "delve","delves","delving","tapestry","testament to","vibrant","pivotal","crucial","landscape of",
 "showcase","showcases","showcasing","underscore","underscores","underscoring","elevate","elevates",
 "elevating","robust","unlock","unlocks","unlocking","empower","empowers","empowering","game-changer",
 "game changer","seamless","seamlessly","cutting-edge","state-of-the-art","holistic","paradigm",
 "revolutionize","revolutionizing","transformative","unparalleled","myriad","plethora","harness",
 "harnessing","navigate the","realm of","in today's","fast-paced world","ever-evolving"];

const CHATBOT = ["i hope this helps","let me know if","great question","happy to help",
 "here's a breakdown","here's a quick","in conclusion","to sum up","hope that helps",
 "feel free to","i'd be happy to","that's a great","certainly!","absolutely!"];

const WEASEL = ["experts agree","studies show","research shows","it is widely known",
 "many people believe","it's no secret","studies have shown","research suggests","data shows"];

const esc = s => s.replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));

function findAll(text, needles){
  const low = text.toLowerCase(), hits = [];
  for(const n of needles){
    let i = 0;
    while((i = low.indexOf(n, i)) !== -1){
      const before = low[i-1], after = low[i+n.length];
      const wordish = c => c && /[a-z0-9]/.test(c);
      if(!wordish(before) && !wordish(after)) hits.push({term:text.substr(i,n.length), at:i});
      i += n.length;
    }
  }
  return hits;
}
