from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else 'extracted/EspritLibreAndroid')
p=root/'app/src/main/assets/index.html'
s=p.read_text(encoding='utf-8')
old='function loadState(){ /* première connexion : données réinitialisées */ }'
new='''function loadState(){
  const raw=localStorage.getItem("esprit_leger_premiere_connexion");
  if(!raw)return;
  try{
    const d=JSON.parse(raw)||{};
    if(d.mood)mood=d.mood;if(d.view)view=d.view;if(d.weather)weather=d.weather;if(d.theme)theme=d.theme;
    if(typeof d.isPremium==="boolean")isPremium=d.isPremium;
    events.splice(0,events.length,...(Array.isArray(d.events)?d.events:[]));
    floating.splice(0,floating.length,...(Array.isArray(d.floating)?d.floating:[]));
    thoughts.splice(0,thoughts.length,...(Array.isArray(d.thoughts)?d.thoughts:[]));
    weekTemplates.splice(0,weekTemplates.length,...(Array.isArray(d.weekTemplates)?d.weekTemplates:[]));
    appNotes.splice(0,appNotes.length,...(Array.isArray(d.appNotes)?d.appNotes:[]));
    Object.keys(people).forEach(k=>delete people[k]);
    if(d.people&&typeof d.people==="object")Object.entries(d.people).forEach(([k,v])=>people[k]=v);
    if(typeof d.onboardingSeen==="boolean")onboardingSeen=d.onboardingSeen;
    if(typeof d.familyIntroSeen==="boolean")familyIntroSeen=d.familyIntroSeen;
    if(d.familyProfile&&typeof d.familyProfile==="object")familyProfile={...familyProfile,...d.familyProfile};
    if(d.liveWeather)liveWeather=d.liveWeather;
    if(typeof d.liveWeatherEnabled==="boolean")liveWeatherEnabled=d.liveWeatherEnabled;
    if(d.selectedDate){const dt=new Date(d.selectedDate);if(!isNaN(dt))selectedDate=dt;}
  }catch(e){console.warn("State restore failed",e);}
}'''
if old not in s: raise SystemExit('loadState placeholder not found')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
print('V6.2 state persistence applied')
