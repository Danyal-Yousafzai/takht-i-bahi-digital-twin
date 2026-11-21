// Takht-i-Bahi AI Digital Twin — KPITB AI Challenge 2026
// Three.js scene · time-warp cross-fade · 3D Orbit / Live AR · multilingual hotspots · photo capture
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/* ------------------------------------------------------------------ */
/* i18n                                                               */
/* ------------------------------------------------------------------ */
const I18N = {
  en: {
    tagline: 'AI Digital Twin · UNESCO World Heritage',
    modeOrbit: '3D Orbit', modeAR: 'Live AR',
    loaderSub: 'Reconstructing the Stupa Court…',
    timeWarp: 'Time-Warp', endNow: '2026 Ruins', endPast: '2nd Century CE',
    eraNow: '2026 CE · Ruins', eraPast: 'c. 150 CE · Kushan Gandhara', eraMid: 'Travelling back · c. {y} CE',
    listen: 'Listen', stop: 'Stop', xray: 'X-ray view',
    arAlign: 'Drag to align · pinch to scale', arAlignGps: 'On-site · drag to fine-tune heading', arLook: 'Drag to look around',
    arRecenter: 'Re-centre', arGhost: 'Ghost ruins',
    save: 'Save photo', share: 'Share', close: 'Close',
    aboutTitle: 'About this Digital Twin',
    aboutBody: 'The 2026 ruins are a photogrammetry scan of the Stupa Court re-centred on the Main Stupa plinth. The 2nd-century reconstruction is generated procedurally on the same origin, so both layers line up exactly.',
    toastNoCam: 'Camera unavailable. Live AR needs a phone camera over HTTPS (or localhost).',
    toastInsecure: 'Live AR needs a secure (HTTPS) connection for the camera.',
    toastNoFs: 'Full screen is not supported on this browser.',
    toastNoVoice: 'No {lang} voice is installed on this device. Using the default voice.',
    toastNoSpeech: 'Speech is not supported on this browser.',
    toastOnsite: 'You are {d} m from the Main Stupa. The past is anchored around you.',
    toastPreview: 'Not on site: the stupa is placed in front of you.',
    toastSaved: 'Photo ready!',
    langName: 'English',
    facts: { plinth: 'Plinth (measured)', drum: 'Drum radius', height: 'Stupa height', faces: 'Scan faces', gps: 'Plinth GPS', crs: 'Survey CRS' },
  },
  ur: {
    tagline: 'اے آئی ڈیجیٹل ٹوئن · یونیسکو عالمی ورثہ',
    modeOrbit: 'تھری ڈی منظر', modeAR: 'لائیو اے آر',
    loaderSub: 'اسٹوپا کورٹ کی تعمیرِ نو ہو رہی ہے…',
    timeWarp: 'وقت کا سفر', endNow: '2026 کھنڈرات', endPast: 'دوسری صدی عیسوی',
    eraNow: '2026ء · کھنڈرات', eraPast: 'تقریباً 150ء · کُشان گندھارا', eraMid: 'ماضی کی طرف سفر · تقریباً {y}ء',
    listen: 'سنیں', stop: 'روکیں', xray: 'ایکسرے منظر',
    arAlign: 'سمت کے لیے گھسیٹیں · سائز کے لیے چٹکی', arAlignGps: 'موقع پر · سمت درست کرنے کے لیے گھسیٹیں', arLook: 'ارد گرد دیکھنے کے لیے گھسیٹیں',
    arRecenter: 'دوبارہ مرکز', arGhost: 'کھنڈرات دکھائیں',
    save: 'تصویر محفوظ کریں', share: 'شیئر کریں', close: 'بند کریں',
    aboutTitle: 'اس ڈیجیٹل ٹوئن کے بارے میں',
    aboutBody: '2026 کے کھنڈرات اسٹوپا کورٹ کا فوٹوگرامیٹری اسکین ہیں جسے مرکزی اسٹوپا کے چبوترے پر مرکوز کیا گیا ہے۔ دوسری صدی کی تعمیرِ نو اسی مرکز پر بنائی گئی ہے، اس لیے دونوں تہیں بالکل ایک دوسرے پر بیٹھتی ہیں۔',
    toastNoCam: 'کیمرا دستیاب نہیں۔ لائیو اے آر کے لیے فون کیمرا اور HTTPS درکار ہے۔',
    toastInsecure: 'کیمرے کے لیے محفوظ (HTTPS) کنکشن درکار ہے۔',
    toastNoFs: 'یہ براؤزر فل اسکرین کی سہولت نہیں دیتا۔',
    toastNoVoice: 'اس آلے پر {lang} آواز موجود نہیں۔ پہلے سے طے شدہ آواز استعمال ہو رہی ہے۔',
    toastNoSpeech: 'یہ براؤزر آواز کی سہولت نہیں دیتا۔',
    toastOnsite: 'آپ مرکزی اسٹوپا سے {d} میٹر دور ہیں۔ ماضی آپ کے ارد گرد موجود ہے۔',
    toastPreview: 'آپ موقع پر نہیں ہیں: اسٹوپا آپ کے سامنے رکھا گیا ہے۔',
    toastSaved: 'تصویر تیار ہے!',
    langName: 'اردو',
    facts: { plinth: 'چبوترا (پیمائش)', drum: 'ڈرم کا رداس', height: 'اسٹوپا کی اونچائی', faces: 'اسکین فیسز', gps: 'جی پی ایس', crs: 'سروے نظام' },
  },
  ps: {
    tagline: 'AI ډیجیټل ټوین · د یونسکو نړیوال میراث',
    modeOrbit: 'درې اړخیز لید', modeAR: 'ژوندی AR',
    loaderSub: 'د سټوپا انګړ بیا جوړېږي…',
    timeWarp: 'د وخت سفر', endNow: '2026 کنډوالې', endPast: 'دویمه عیسوي پېړۍ',
    eraNow: '2026 ز · کنډوالې', eraPast: 'شاوخوا 150 ز · کوشاني ګندهارا', eraMid: 'تېر وخت ته سفر · شاوخوا {y} ز',
    listen: 'واورئ', stop: 'ودروئ', xray: 'ایکسرې لید',
    arAlign: 'د لوري لپاره کش کړئ · د اندازې لپاره چونډی', arAlignGps: 'په ځای کې · د لوري سمولو لپاره کش کړئ', arLook: 'شاوخوا لیدو لپاره کش کړئ',
    arRecenter: 'بیا منځ ته', arGhost: 'کنډوالې وښایاست',
    save: 'انځور خوندي کړئ', share: 'شریک کړئ', close: 'بند کړئ',
    aboutTitle: 'د دې ډیجیټل ټوین په اړه',
    aboutBody: 'د 2026 کنډوالې د سټوپا انګړ فوټوګرامیټري سکین دی چې د لوی سټوپا پر چبوتره منځ ته راوړل شوی. د دویمې پېړۍ بیارغونه په همدې منځ جوړه شوې، نو دواړه پوړونه سم پر یو بل کېني.',
    toastNoCam: 'کیمره نشته. ژوندي AR ته د تلیفون کیمره او HTTPS اړتیا ده.',
    toastInsecure: 'کیمرې ته خوندي (HTTPS) اړیکه اړینه ده.',
    toastNoFs: 'دا براوزر بشپړه پرده نه ملاتړ کوي.',
    toastNoVoice: 'په دې وسیله {lang} غږ نشته. اصلي غږ کارول کېږي.',
    toastNoSpeech: 'دا براوزر غږ نه ملاتړ کوي.',
    toastOnsite: 'تاسو له لوی سټوپا {d} متره لرې یاست. تېر وخت ستاسو شاوخوا دی.',
    toastPreview: 'تاسو په ځای کې نه یاست: سټوپا ستاسو مخې ته ایښودل شوی.',
    toastSaved: 'انځور چمتو دی!',
    langName: 'پښتو',
    facts: { plinth: 'چبوتره (اندازه)', drum: 'د ډرم شعاع', height: 'د سټوپا لوړوالی', faces: 'د سکین مخونه', gps: 'GPS', crs: 'د سروې سیسټم' },
  },
};

const HOTSPOTS = {
  stupa: {
    icon: '1',
    en: { kicker: 'Stupa Court · Main Stupa', title: 'The Main Stupa',
      body: 'At the heart of the Stupa Court stood the monastery’s most sacred monument. A square plinth with a north stairway carried a moulded drum, the hemispherical dome (anda), the railed harmika and a mast of five tiered umbrellas (chattras). Pilgrims walked clockwise around it in pradakshina. Takht-i-Bahi was founded in the 1st century CE and flourished under the Kushans until about the 7th century.' },
    ur: { kicker: 'اسٹوپا کورٹ · مرکزی اسٹوپا', title: 'مرکزی اسٹوپا',
      body: 'اسٹوپا کورٹ کے بیچ میں کھڑا یہ اسٹوپا خانقاہ کی سب سے مقدس یادگار تھا۔ شمالی سیڑھی والے مربع چبوترے پر ایک نقش دار ڈرم، نیم کروی گنبد (انڈا)، جنگلے دار ہرمیکا اور پانچ منزلہ چھتریوں والا ستون قائم تھا۔ زائرین اس کے گرد گھڑی کی سمت میں طواف کرتے تھے۔ تختِ بائی کی بنیاد پہلی صدی عیسوی میں رکھی گئی اور یہ کُشان دور سے ساتویں صدی تک آباد رہا۔' },
    ps: { kicker: 'د سټوپا انګړ · لوی سټوپا', title: 'لوی سټوپا',
      body: 'د سټوپا انګړ په منځ کې دا سټوپا د خانقاه تر ټولو سپېڅلې ودانۍ وه. د شمالي زینو لرونکې څلورګوټې چبوترې پر سر یو نقش لرونکی ډرم، نیم ګردی ګنبد (انډا)، کټاره لرونکې هرمیکا او د پنځو پوړیزو چترونو ستن ولاړه وه. زیارت کوونکو به یې د ساعت د ستنې په لور طواف کاوه. تخت بهائي په لومړۍ عیسوي پېړۍ کې جوړ شو او د کوشانیانو له دورې تر اوومې پېړۍ پورې آباد و.' },
  },
  relic: {
    icon: '2', xray: true,
    en: { kicker: 'Inside the drum', title: 'Relic Chamber',
      body: 'Deep inside the drum lay the relic chamber — the reason a stupa exists. Sealed reliquaries of schist, crystal or gold held sacred relics such as bone, ash or texts, enshrining the presence of the Buddha. Switch on X-ray view to see the casket hidden in the core.' },
    ur: { kicker: 'ڈرم کے اندر', title: 'تبرکات کا حجرہ',
      body: 'ڈرم کے اندر گہرائی میں تبرکات کا حجرہ تھا، جو اسٹوپا کی تعمیر کی اصل وجہ ہے۔ شیسٹ پتھر، بلور یا سونے کے مہر بند صندوقچوں میں مقدس تبرکات رکھے جاتے تھے۔ اندر چھپا صندوقچہ دیکھنے کے لیے ایکسرے منظر کھولیں۔' },
    ps: { kicker: 'د ډرم دننه', title: 'د تبرکاتو خونه',
      body: 'د ډرم په ژور کې د تبرکاتو خونه وه، چې د سټوپا د جوړولو اصلي موخه ده. د شیسټ ډبرې، بلور یا سرو زرو په تړلو صندوقچو کې سپېڅلي تبرکات ساتل کېدل. دننه پټه صندوقچه د لیدو لپاره ایکسرې لید پرانیزئ.' },
  },
  niche: {
    icon: '3',
    en: { kicker: 'Chapels of the court', title: 'Buddha Niches',
      body: 'Small chapels with arched caitya façades ring the court on three sides. Each housed a Buddha or Bodhisattva in schist or lime stucco, often gilded or painted. Here the Buddha sits in dhyana mudra, the gesture of meditation — a hallmark of Gandharan art, where Greco-Roman and South Asian traditions met.' },
    ur: { kicker: 'صحن کے عبادت خانے', title: 'بدھا کے طاق',
      body: 'صحن کے تین اطراف محراب دار چیتیہ طرز کے چھوٹے عبادت خانے ہیں۔ ہر ایک میں شیسٹ پتھر یا چونے کے پلستر سے بنی بدھا یا بودھی ستوا کی مورتی ہوتی تھی، جن پر اکثر سنہری رنگ کیا جاتا تھا۔ یہاں بدھا دھیان مدرا یعنی مراقبے کی حالت میں بیٹھے ہیں۔ یہ گندھارا فن کی پہچان ہے، جہاں یونانی، رومی اور جنوبی ایشیائی روایات آپس میں ملیں۔' },
    ps: { kicker: 'د انګړ عبادت ځایونه', title: 'د بودا طاقونه',
      body: 'د انګړ په دریو خواوو کې د محراب لرونکو چیتیا مخونو کوچني عبادت ځایونه دي. په هر یوه کې به د شیسټ ډبرې یا چونې د بودا یا بودیستوا مجسمه وه چې ډېری وخت به زرینه رنګ شوې وه. دلته بودا د دهیان مدرا، یعنې د مراقبې په حالت کې ناست دی. دا د ګندهارا هنر نښه ده چې یوناني، رومي او سویلي آسیايي دودونه پکې سره یوځای شول.' },
  },
};

/* ------------------------------------------------------------------ */
/* DOM + state                                                        */
/* ------------------------------------------------------------------ */
const $ = (id) => document.getElementById(id);
const state = {
  lang: 'en', mode: 'orbit', t: 0, xray: false, ghost: false, active: null,
  meta: null, playing: false,
};
const isTouch = matchMedia('(pointer: coarse)').matches;

let toastTimer;
function toast(msg, ms = 3200) {
  const el = $('toast');
  el.textContent = msg;
  el.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.remove('show'), ms);
}
const tr = (k, vars = {}) => (I18N[state.lang][k] ?? I18N.en[k]).replace(/\{(\w+)\}/g, (_, v) => vars[v] ?? '');

/* ------------------------------------------------------------------ */
/* Renderer, scene, lights                                            */
/* ------------------------------------------------------------------ */
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
const BASE_DPR = Math.min(window.devicePixelRatio || 1, isTouch ? 1.75 : 2);
renderer.setPixelRatio(BASE_DPR);
renderer.setSize(innerWidth, innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.2;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
$('stage').appendChild(renderer.domElement);

const scene = new THREE.Scene();
const FOG_COLOR = new THREE.Color(0xeadfca);
scene.fog = new THREE.Fog(FOG_COLOR, 90, 320);

const camera = new THREE.PerspectiveCamera(50, innerWidth / innerHeight, 0.1, 2000);
const HOME = { pos: new THREE.Vector3(-17, 19, 23), target: new THREE.Vector3(0, 2.6, 0) };
// Portrait phones need the camera further back to frame the court
const portraitFactor = () => (camera.aspect < 1 ? Math.pow(1 / camera.aspect, 0.75) : 1);
const homePos = () => HOME.target.clone().add(HOME.pos.clone().sub(HOME.target).multiplyScalar(portraitFactor()));
camera.position.copy(homePos());

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.copy(HOME.target);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.minDistance = 4;
controls.maxDistance = 110;
controls.maxPolarAngle = THREE.MathUtils.degToRad(86);
controls.screenSpacePanning = true;
controls.update();

// Warm late-afternoon sun from the south-west
const SUN_DIR = new THREE.Vector3(-0.55, 0.62, 0.56).normalize();

// Gradient sky dome with a sun glow
const sky = new THREE.Mesh(
  new THREE.SphereGeometry(900, 32, 16),
  new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false, fog: false,
    uniforms: {
      top: { value: new THREE.Color(0x2f6fc4) }, horizon: { value: new THREE.Color(0xf4e6cc) },
      bottom: { value: new THREE.Color(0xb89772) }, sunDir: { value: SUN_DIR },
    },
    vertexShader: 'varying vec3 vDir; void main(){ vDir = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }',
    fragmentShader: `uniform vec3 top, horizon, bottom, sunDir; varying vec3 vDir;
      void main(){
        float h = vDir.y;
        vec3 c = h > 0.0 ? mix(horizon, top, pow(smoothstep(0.0, 0.5, h), 0.6)) : mix(horizon, bottom, smoothstep(0.0, -0.25, h));
        float s = max(dot(normalize(vDir), normalize(sunDir)), 0.0);
        c += vec3(1.0, 0.82, 0.55) * (pow(s, 600.0) * 4.0 + pow(s, 12.0) * 0.28);
        gl_FragColor = vec4(c, 1.0);
        #include <colorspace_fragment>
      }`,
  }),
);
sky.renderOrder = -1;
scene.add(sky);

// Environment map from the sky (gives the gilded Buddhas their sheen)
{
  const pmrem = new THREE.PMREMGenerator(renderer);
  const envScene = new THREE.Scene();
  envScene.add(sky.clone());
  scene.environment = pmrem.fromScene(envScene, 0.02).texture;
  scene.environmentIntensity = 0.4;
  pmrem.dispose();
}

const hemi = new THREE.HemisphereLight(0xeaf2ff, 0x6a5640, 0.8);
scene.add(hemi);
const sun = new THREE.DirectionalLight(0xffdfb0, 3.1);
sun.position.copy(SUN_DIR).multiplyScalar(80);
sun.castShadow = true;
sun.shadow.mapSize.set(isTouch ? 1024 : 2048, isTouch ? 1024 : 2048);
Object.assign(sun.shadow.camera, { left: -32, right: 32, top: 32, bottom: -32, near: 10, far: 200 });
sun.shadow.bias = -0.0004;
sun.shadow.normalBias = 0.04;
scene.add(sun, sun.target);

/* Scene graph:  scene > arWorld (heading correction about the user) > site (ruins + recon + anchors) */
const arWorld = new THREE.Group();
const site = new THREE.Group();
arWorld.add(site);
scene.add(arWorld);

// Soft ground disc under the hill-top scan (fades into the fog)
let ground;

/* ------------------------------------------------------------------ */
/* Loading                                                            */
/* ------------------------------------------------------------------ */
const DEFAULT_META = {
  origin_latlon: [34.28608, 71.946978], crs: 'EPSG:32642',
  plinth: { width_ew: 6.5, depth_ns: 6.75, height: 1.47 },
  court: { court_w: -7.2, court_e: 6.95, court_s: -6.83, court_n: 10.82 },
  drum_radius: 2.95, stupa_height: 9.65, ruins_faces: 135706,
  ruins_bounds: [[-39.9, -16.5, -44.5], [46.6, 16.3, 29.7]],
  hotspots: { stupa: [0, 6.1, 0], relic: [0, 2.37, 3.2], niche: [-8.85, 1.75, -3.47] },
};

const progress = { ruins: 0, recon: 0 };
function setProgress() {
  const p = Math.round((progress.ruins * 0.48 + progress.recon * 0.52) * 100);
  $('progressBar').style.width = p + '%';
  $('progressText').textContent = p + '%';
}

function loadGLB(url, key) {
  const loader = new GLTFLoader();
  return new Promise((resolve, reject) => {
    loader.load(
      url,
      (g) => {
        progress[key] = 1;
        setProgress();
        resolve(g.scene);
      },
      (e) => {
        if (e.total) {
          // GitHub Pages gzips responses, so `loaded` can exceed `total`: cap below 100 %
          progress[key] = Math.min(e.loaded / e.total, 0.99);
          setProgress();
        }
      },
      reject
    );
  });
}

const texLoader = new THREE.TextureLoader();
const stoneTex = texLoader.load('assets/gandhara_stone_wall.jpg');
stoneTex.wrapS = THREE.RepeatWrapping;
stoneTex.wrapT = THREE.RepeatWrapping;
if (THREE.SRGBColorSpace) stoneTex.colorSpace = THREE.SRGBColorSpace;

let ruins, recon;
const ruinsUniforms = {
  uFade: { value: 0 },
  uCourtMin: { value: new THREE.Vector2() },
  uCourtMax: { value: new THREE.Vector2() },
  uStoneTex: { value: stoneTex },
};
const reconMats = [];
const anchors = {};

async function init() {
  try {
    const r = await fetch('assets/scene_meta.json', { cache: 'no-cache' });
    state.meta = r.ok ? await r.json() : DEFAULT_META;
  } catch { state.meta = DEFAULT_META; }
  const M = state.meta;

  // Court fade region (glTF coords: north = -Z). Chapels are 2.6 m deep.
  const c = M.court;
  ruinsUniforms.uCourtMin.value.set(c.court_w - 3.1, -(c.court_n + 2.0));
  ruinsUniforms.uCourtMax.value.set(c.court_e + 3.1, -(c.court_s - 3.1));

  let ruinsScene, reconScene;
  try {
    [ruinsScene, reconScene] = await Promise.all([
      loadGLB('assets/ruins.glb?v=2', 'ruins'),
      loadGLB('assets/reconstructed.glb', 'recon'),
    ]);
  } catch (err) {
    console.error(err);
    $('loader').querySelector('.loader-sub').textContent =
      'Could not load assets/*.glb — run process_mesh.py and serve with: python -m http.server 8000';
    return;
  }

  // --- Ruins: photographic stone (baked into ruins.glb) × baked cavity AO, with a court fade
  ruins = ruinsScene;
  const ruinsMats = [];
  const patchRuinsMat = (src) => {
    // keep the embedded photo texture (map) and the COLOR_0 cavity/AO from the GLB
    const mat = new THREE.MeshStandardMaterial({
      map: src.map || null, vertexColors: true,
      roughness: 0.94, metalness: 0, transparent: false, name: src.name,
    });
    if (mat.map) {
      mat.map.colorSpace = THREE.SRGBColorSpace;
      mat.map.wrapS = mat.map.wrapT = THREE.RepeatWrapping;
      mat.map.anisotropy = renderer.capabilities.getMaxAnisotropy();
      mat.map.needsUpdate = true;
    }
    mat.onBeforeCompile = (shader) => {
      Object.assign(shader.uniforms, ruinsUniforms);
      // object-space position == site-local metres (the ruins nodes have an identity transform)
      shader.vertexShader = 'varying vec3 vLocal;\n' + shader.vertexShader.replace(
        '#include <project_vertex>',
        '#include <project_vertex>\n vLocal = transformed;');
      shader.fragmentShader = 'uniform float uFade; uniform vec2 uCourtMin, uCourtMax; varying vec3 vLocal;\n' +
        shader.fragmentShader
          // map_fragment has multiplied in the photo; color_fragment then multiplies the AO.
          // Deepen the photo's own dark joints (mortar, cracks) so they read as recesses.
          .replace('#include <map_fragment>', `#include <map_fragment>
        #ifdef USE_MAP
          float lum = dot(diffuseColor.rgb, vec3(0.299, 0.587, 0.114));
          diffuseColor.rgb *= mix(0.45, 1.0, smoothstep(0.03, 0.30, lum));
        #endif`)
          .replace('#include <color_fragment>', `#include <color_fragment>
        // Time-warp: fade the ruins inside the Stupa Court, warm-tint the rest of the site
        float inX = smoothstep(uCourtMin.x - 1.5, uCourtMin.x, vLocal.x) * (1.0 - smoothstep(uCourtMax.x, uCourtMax.x + 1.5, vLocal.x));
        float inZ = smoothstep(uCourtMin.y - 1.5, uCourtMin.y, vLocal.z) * (1.0 - smoothstep(uCourtMax.y, uCourtMax.y + 1.5, vLocal.z));
        float inside = inX * inZ;
        diffuseColor.rgb = mix(diffuseColor.rgb, diffuseColor.rgb * vec3(1.10, 1.0, 0.86), uFade * (1.0 - inside) * 0.7);
        diffuseColor.a *= mix(1.0, 1.0 - uFade, inside);
        if (diffuseColor.a < 0.02) discard;`);
    };
    ruinsMats.push(mat);
    return mat;
  };
  ruins.traverse((o) => {
    if (!o.isMesh) return;
    o.material = patchRuinsMat(o.material);
    o.castShadow = true; o.receiveShadow = true;
  });
  ruins.userData.mats = ruinsMats;
  site.add(ruins);

  // --- Reconstruction
  recon = reconScene;
  recon.traverse((o) => {
    if (!o.isMesh) return;
    o.castShadow = true; o.receiveShadow = true;
    const m = o.material;
    m.transparent = true; m.depthWrite = true;
    m.userData.baseEmissive = m.emissive.clone();
    m.userData.isPlaster = /Plaster|Ochre/i.test(m.name);
    if (/Gilded|Halo/i.test(m.name)) m.envMapIntensity = 2.2;
    if (m.map) m.map.anisotropy = renderer.capabilities.getMaxAnisotropy();
    reconMats.push(m);
  });
  site.add(recon);

  // Ground disc slightly below the lowest point of the scan
  const yMin = M.ruins_bounds[0][1];
  const g = new THREE.CircleGeometry(400, 64);  // sandy valley floor
  g.rotateX(-Math.PI / 2);
  ground = new THREE.Mesh(g, new THREE.MeshStandardMaterial({ color: 0xc2aa84, roughness: 1 }));
  ground.position.y = yMin - 0.6;
  ground.receiveShadow = true;
  site.add(ground);

  // Hotspot anchors (small glowing beads at each 3-D pin location)
  const bead = new THREE.SphereGeometry(0.14, 16, 12);
  for (const [key, p] of Object.entries(M.hotspots)) {
    const a = new THREE.Mesh(bead, new THREE.MeshBasicMaterial({ color: 0xffd98a, toneMapped: false, transparent: true, opacity: 0.9, depthTest: false }));
    a.renderOrder = 10;
    a.position.fromArray(p);
    site.add(a);
    anchors[key] = a;
  }
  buildPins();
  buildFacts();
  setTime(0);

  $('loader').classList.add('done');
  setTimeout(() => $('loader').remove(), 800);
}

/* ------------------------------------------------------------------ */
/* Time-warp                                                          */
/* ------------------------------------------------------------------ */
function setTime(t) {
  state.t = t = THREE.MathUtils.clamp(t, 0, 1);
  const slider = $('slider');
  slider.value = (t * 100).toFixed(1);
  slider.style.setProperty('--p', t * 100 + '%');
  $('pctText').textContent = Math.round(t * 100) + '%';
  updateEraText();

  // In AR the real ruins are seen through the camera: only the past is overlaid.
  const ruinsFade = state.mode === 'ar' ? 1 : t;
  if (ruins) {
    ruinsUniforms.uFade.value = ruinsFade;
    const tr_ = ruinsFade > 0.001;
    for (const mat of ruins.userData.mats || []) {
      if (mat.transparent !== tr_) { mat.transparent = tr_; mat.needsUpdate = true; }
    }
    ruins.visible = state.mode !== 'ar' || state.ghost;
    if (state.mode === 'ar' && state.ghost) ruinsUniforms.uFade.value = 0.55;
  }
  if (recon) {
    const k = state.xray ? 1 : t;
    recon.visible = k > 0.002;
    const glow = Math.sin(Math.PI * t) * 0.35;
    for (const m of reconMats) {
      let op = k;
      if (state.xray && m.userData.isPlaster) op = 0.22;
      m.opacity = op;
      const tr_ = op < 0.999;
      if (m.transparent !== tr_) { m.transparent = tr_; m.needsUpdate = true; }
      m.depthWrite = op > 0.5;
      m.emissive.copy(m.userData.baseEmissive).lerp(new THREE.Color(0xffb347), glow);
    }
  }
}
function findMat(root) { let mat = null; root.traverse((o) => { if (o.isMesh && !mat) mat = o.material; }); return mat; }

function updateEraText() {
  const t = state.t;
  let s;
  if (t < 0.03) s = tr('eraNow');
  else if (t > 0.97) s = tr('eraPast');
  else s = tr('eraMid', { y: Math.round(2026 - t * (2026 - 150)) });
  $('eraText').textContent = s;
}

$('slider').addEventListener('input', (e) => { state.playing = false; setPlayIcon(); setTime(e.target.value / 100); });

let playFrom = 0, playTo = 1, playStart = 0;
function setPlayIcon() {
  $('btnPlay').innerHTML = state.playing
    ? '<svg viewBox="0 0 24 24"><path d="M7 5h4v14H7zM13 5h4v14h-4z"/></svg>'
    : '<svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>';
}
$('btnPlay').addEventListener('click', () => {
  state.playing = !state.playing;
  if (state.playing) {
    playFrom = state.t; playTo = state.t > 0.5 ? 0 : 1; playStart = performance.now();
  }
  setPlayIcon();
});
function stepPlay(now) {
  if (!state.playing) return;
  const dur = 4200 * Math.abs(playTo - playFrom) + 1;
  const k = Math.min((now - playStart) / dur, 1);
  const e = k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2;
  setTime(playFrom + (playTo - playFrom) * e);
  if (k >= 1) { state.playing = false; setPlayIcon(); }
}

/* ------------------------------------------------------------------ */
/* Hotspot pins + narration                                           */
/* ------------------------------------------------------------------ */
const pinEls = {};
function buildPins() {
  const wrap = $('pins');
  for (const key of Object.keys(anchors)) {
    const b = document.createElement('button');
    b.className = 'pin';
    b.innerHTML = `<span class="pin-label"></span><span class="pin-dot"><b>${HOTSPOTS[key]?.icon ?? '•'}</b></span>`;
    b.addEventListener('click', (e) => { e.stopPropagation(); openCard(key); });
    wrap.appendChild(b);
    pinEls[key] = b;
  }
  refreshPinLabels();
}
function refreshPinLabels() {
  for (const [k, el] of Object.entries(pinEls)) {
    el.querySelector('.pin-label').textContent = HOTSPOTS[k][state.lang].title;
    el.setAttribute('aria-label', HOTSPOTS[k][state.lang].title);
  }
}

const _v = new THREE.Vector3();
function updatePins() {
  const w = innerWidth, h = innerHeight;
  for (const [k, el] of Object.entries(pinEls)) {
    anchors[k].getWorldPosition(_v);
    const dist = _v.distanceTo(camera.position);
    _v.project(camera);
    const visible = _v.z < 1 && _v.z > -1 && Math.abs(_v.x) < 1.15 && Math.abs(_v.y) < 1.15;
    el.style.display = visible ? '' : 'none';
    if (!visible) continue;
    const x = (_v.x * 0.5 + 0.5) * w, y = (-_v.y * 0.5 + 0.5) * h;
    const s = THREE.MathUtils.clamp(28 / dist, 0.7, 1.1);
    el.style.transform = `translate(${x}px, ${y}px) translate(-50%, -100%) scale(${s.toFixed(3)})`;
  }
}

function openCard(key) {
  state.active = key;
  const d = HOTSPOTS[key][state.lang];
  $('cardKicker').textContent = d.kicker;
  $('cardTitle').textContent = d.title;
  $('cardBody').textContent = d.body;
  $('btnXray').hidden = !HOTSPOTS[key].xray;
  $('card').hidden = false;
  for (const [k, el] of Object.entries(pinEls)) el.classList.toggle('active', k === key);
  if (state.mode === 'orbit') flyTo(key);
  stopSpeech();
}
function closeCard() {
  $('card').hidden = true;
  state.active = null;
  for (const el of Object.values(pinEls)) el.classList.remove('active');
  stopSpeech();
  if (state.xray) toggleXray(false);
}
$('cardClose').addEventListener('click', closeCard);

function toggleXray(on = !state.xray) {
  state.xray = on;
  $('btnXray').classList.toggle('speaking', on);
  setTime(state.t);
}
$('btnXray').addEventListener('click', () => toggleXray());

// Narration: pre-rendered neural-voice MP3s (assets/audio, made by generate_audio.py),
// falling back to the Web Speech API when a file is missing or can't play.
// (Most phones / PCs ship no Urdu or Pashto TTS voice, so the MP3s are the main path.)
const AUDIO_VERSION = 1;               // bump after re-running generate_audio.py
let narrAudio = null;                  // current HTMLAudioElement
let narrToken = 0;                     // invalidates callbacks from a stopped narration
let narrating = false;
const SPEECH_LANGS = { en: ['en-GB', 'en-US', 'en-IN', 'en'], ur: ['ur-PK', 'ur-IN', 'ur'], ps: ['ps-AF', 'ps-PK', 'ps', 'ur-PK', 'ur', 'fa-IR', 'fa'] };
function pickVoice(lang) {
  const voices = speechSynthesis.getVoices();
  for (const code of SPEECH_LANGS[lang]) {
    const v = voices.find((x) => x.lang.replace('_', '-').toLowerCase().startsWith(code.toLowerCase()));
    if (v) return v;
  }
  return null;
}
if ('speechSynthesis' in window) speechSynthesis.onvoiceschanged = () => {};
function setSpeakButton(on) {
  narrating = on;
  $('btnSpeak').classList.toggle('speaking', on);
  $('btnSpeak').querySelector('span').textContent = tr(on ? 'stop' : 'listen');
}
function stopSpeech() {
  narrToken++;
  if (narrAudio) {
    narrAudio.pause();
    narrAudio.removeAttribute('src');
    narrAudio.load();
    narrAudio = null;
  }
  if ('speechSynthesis' in window) speechSynthesis.cancel();
  setSpeakButton(false);
}
function speakWithTTS(key, lang, token) {
  if (token !== narrToken) return;
  if (!('speechSynthesis' in window)) { setSpeakButton(false); return toast(tr('toastNoSpeech')); }
  const d = HOTSPOTS[key][lang];
  const u = new SpeechSynthesisUtterance(`${d.title}. ${d.body}`);
  const v = pickVoice(lang);
  u.lang = SPEECH_LANGS[lang][0];
  if (v) { u.voice = v; u.lang = v.lang; } else if (lang !== 'en') toast(tr('toastNoVoice', { lang: tr('langName') }));
  u.rate = lang === 'en' ? 0.98 : 0.92;
  u.onend = u.onerror = () => { if (token === narrToken) setSpeakButton(false); };
  speechSynthesis.speak(u);
}
function playNarration(key, lang) {
  stopSpeech();
  const token = narrToken;
  setSpeakButton(true);
  const audio = new Audio(`assets/audio/${key}_${lang}.mp3?v=${AUDIO_VERSION}`);
  audio.preload = 'auto';
  narrAudio = audio;
  let fellBack = false;
  const fallback = () => {
    if (fellBack || token !== narrToken) return;
    fellBack = true;
    narrAudio = null;
    speakWithTTS(key, lang, token);
  };
  audio.onended = () => { if (token === narrToken) { narrAudio = null; setSpeakButton(false); } };
  audio.onerror = fallback;                       // 404 / unsupported file
  audio.play().catch((err) => {                   // autoplay policy or decode failure
    if (err && err.name === 'AbortError') return; // we stopped it ourselves
    fallback();
  });
}
$('btnSpeak').addEventListener('click', () => {
  if (narrating) return stopSpeech();
  if (state.active) playNarration(state.active, state.lang);
});

/* ------------------------------------------------------------------ */
/* Language                                                           */
/* ------------------------------------------------------------------ */
function setLang(lang) {
  if (narrating) stopSpeech();
  state.lang = lang;
  document.documentElement.lang = lang;
  document.body.classList.toggle('rtl', lang !== 'en');
  document.body.classList.remove('lang-en', 'lang-ur', 'lang-ps');
  document.body.classList.add('lang-' + lang);
  document.querySelectorAll('.lang button').forEach((b) => b.classList.toggle('active', b.dataset.lang === lang));
  document.querySelectorAll('[data-i18n]').forEach((el) => { const k = el.dataset.i18n; if (I18N[lang][k]) el.textContent = I18N[lang][k]; });
  refreshPinLabels();
  updateEraText();
  buildFacts();
  if (state.mode === 'ar') updateArStatus();
  if (state.active) openCard(state.active);
}
document.querySelectorAll('.lang button').forEach((b) => b.addEventListener('click', () => setLang(b.dataset.lang)));

function buildFacts() {
  const M = state.meta; if (!M) return;
  const f = I18N[state.lang].facts;
  $('facts').innerHTML = [
    [f.plinth, `${M.plinth.width_ew} × ${M.plinth.depth_ns} m`],
    [f.drum, `${M.drum_radius} m`],
    [f.height, `${M.stupa_height} m`],
    [f.faces, Number(M.ruins_faces).toLocaleString('en')],
    [f.gps, `${M.origin_latlon[0].toFixed(5)}°N, ${M.origin_latlon[1].toFixed(5)}°E`],
    [f.crs, `${M.crs} (UTM 42N)`],
  ].map(([k, v]) => `<li>${k}<b dir="ltr">${v}</b></li>`).join('');
}

/* ------------------------------------------------------------------ */
/* Camera animation (orbit mode)                                      */
/* ------------------------------------------------------------------ */
let fly = null;
function flyToPose(pos, target, ms = 1400) {
  fly = { p0: camera.position.clone(), t0: controls.target.clone(), p1: pos.clone(), t1: target.clone(), start: performance.now(), ms };
}
function flyTo(key) {
  const a = anchors[key].position.clone();
  const dir = new THREE.Vector3().subVectors(camera.position, controls.target).setY(0).normalize();
  if (key === 'niche') dir.set(1, 0, 0.25).normalize();         // look into the west chapels
  if (key === 'relic') dir.set(0.25, 0, 1).normalize();          // relic pin faces south (+Z)
  const dist = (key === 'stupa' ? 19 : key === 'relic' ? 9 : 8) * portraitFactor();
  const target = key === 'stupa' ? new THREE.Vector3(0, 4, 0) : key === 'relic' ? new THREE.Vector3(0, 2.2, 0) : a.clone();
  const lift = key === 'stupa' ? 7 : key === 'relic' ? 6 : 2.2;
  const pos = target.clone().addScaledVector(dir, dist).add(new THREE.Vector3(0, lift, 0));
  flyToPose(pos, target);
}
function stepFly(now) {
  if (!fly) return;
  const k = Math.min((now - fly.start) / fly.ms, 1);
  const e = 1 - Math.pow(1 - k, 3);
  camera.position.lerpVectors(fly.p0, fly.p1, e);
  controls.target.lerpVectors(fly.t0, fly.t1, e);
  if (k >= 1) fly = null;
}
controls.addEventListener('start', () => { fly = null; });

$('btnReset').addEventListener('click', () => {
  if (state.mode === 'ar') return arRecenter();
  flyToPose(homePos(), HOME.target);
});

/* ------------------------------------------------------------------ */
/* Live AR mode: camera feed + device orientation (+ GPS on site)     */
/* ------------------------------------------------------------------ */
const ar = {
  stream: null, hasGyro: false, onsite: false, geoWatch: null,
  alpha: 0, beta: 90, gamma: 0, headingOffset: null, absolute: false,
  lookYaw: 0, lookPitch: 0, userENU: new THREE.Vector3(), targetENU: new THREE.Vector3(),
  scale: 1, saved: null,
};
const EYE = 1.6;

function onOrient(e) {
  if (e.alpha == null) return;
  ar.hasGyro = true;
  ar.beta = e.beta; ar.gamma = e.gamma;
  if (e.type === 'deviceorientationabsolute' || e.absolute) {
    ar.absolute = true; ar.alpha = e.alpha;
  } else if (!ar.absolute) {
    // iOS: derive compass-referenced alpha from webkitCompassHeading
    if (typeof e.webkitCompassHeading === 'number') {
      const target = (360 - e.webkitCompassHeading - e.alpha + 720) % 360;
      if (ar.headingOffset == null) ar.headingOffset = target;
      else {
        let d = ((target - ar.headingOffset + 540) % 360) - 180;
        ar.headingOffset = (ar.headingOffset + d * 0.02 + 360) % 360;
      }
    }
    ar.alpha = e.alpha + (ar.headingOffset ?? 0);
  }
}

const _euler = new THREE.Euler(), _q0 = new THREE.Quaternion(), _zee = new THREE.Vector3(0, 0, 1);
const _q1 = new THREE.Quaternion(-Math.sqrt(0.5), 0, 0, Math.sqrt(0.5));
function applyDeviceOrientation() {
  const deg = THREE.MathUtils.degToRad;
  const orient = deg(screen.orientation?.angle ?? window.orientation ?? 0);
  _euler.set(deg(ar.beta), deg(ar.alpha), -deg(ar.gamma), 'YXZ');
  camera.quaternion.setFromEuler(_euler);
  camera.quaternion.multiply(_q1);
  camera.quaternion.multiply(_q0.setFromAxisAngle(_zee, -orient));
}

function updateArStatus() {
  $('arStatus').textContent = !ar.hasGyro ? tr('arLook') : ar.onsite ? tr('arAlignGps') : tr('arAlign');
}

function arRecenter() {
  if (ar.onsite) { arWorld.rotation.y = 0; return; }
  // place the stupa in front of the current gaze, at real scale ~26 m away
  const fwd = new THREE.Vector3(0, 0, -1).applyQuaternion(camera.quaternion).setY(0);
  if (fwd.lengthSq() < 1e-4) fwd.set(0, 0, -1);
  fwd.normalize();
  const dist = 4 + 26 * ar.scale;
  arWorld.rotation.y = 0;
  site.position.copy(camera.position).addScaledVector(fwd, dist);
  site.position.y = ar.scale < 0.3 ? EYE - 1.0 : 0;
  site.rotation.y = Math.atan2(fwd.x, fwd.z);   // face the court entrance toward the user
  site.scale.setScalar(ar.scale);
}

async function enterAR() {
  if (!window.isSecureContext) { toast(tr('toastInsecure'), 4500); return; }
  if (!navigator.mediaDevices?.getUserMedia) { toast(tr('toastNoCam'), 4500); return; }

  // iOS needs both permission prompts inside the same user gesture
  const orientPerm = (typeof DeviceOrientationEvent !== 'undefined' && typeof DeviceOrientationEvent.requestPermission === 'function')
    ? DeviceOrientationEvent.requestPermission().catch(() => 'denied') : Promise.resolve('granted');
  let stream;
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: { ideal: 'environment' }, width: { ideal: 1920 }, height: { ideal: 1080 } }, audio: false,
    });
  } catch (err) {
    console.warn(err); toast(tr('toastNoCam'), 4500); return;
  }
  await orientPerm;

  ar.stream = stream;
  const video = $('camera');
  video.srcObject = stream;
  await video.play().catch(() => {});

  ar.saved = { pos: camera.position.clone(), target: controls.target.clone(), fov: camera.fov };
  state.mode = 'ar';
  document.body.classList.add('ar');
  setModeButtons();
  controls.enabled = false;
  fly = null;
  sky.visible = false; ground.visible = false;
  scene.fog = null;
  renderer.setClearColor(0x000000, 0);
  camera.position.set(0, EYE, 0);
  camera.quaternion.identity();
  camera.fov = 60; camera.updateProjectionMatrix();
  ar.scale = 1; ar.lookYaw = 0; ar.lookPitch = 0; ar.headingOffset = null; ar.absolute = false; ar.hasGyro = false;
  if (state.t < 0.5) setTime(1); else setTime(state.t);

  window.addEventListener('deviceorientationabsolute', onOrient);
  window.addEventListener('deviceorientation', onOrient);

  $('arHint').hidden = false;
  updateArStatus();
  arRecenter();
  setTimeout(() => { updateArStatus(); if (!ar.onsite) arRecenter(); }, 900);

  // GPS: if the visitor is on site, anchor the model to the real coordinates
  if (navigator.geolocation && state.meta) {
    ar.geoWatch = navigator.geolocation.watchPosition((pos) => {
      const [lat0, lon0] = state.meta.origin_latlon;
      const dN = (pos.coords.latitude - lat0) * 111320;
      const dE = (pos.coords.longitude - lon0) * 111320 * Math.cos(THREE.MathUtils.degToRad(lat0));
      const d = Math.hypot(dN, dE);
      const wasOnsite = ar.onsite;
      ar.onsite = d < 450 && pos.coords.accuracy < 60;
      ar.targetENU.set(dE, 0, -dN);
      if (ar.onsite && !wasOnsite) {
        ar.userENU.copy(ar.targetENU);
        ar.scale = 1;
        site.rotation.y = 0; site.scale.setScalar(1);
        toast(tr('toastOnsite', { d: Math.round(d) }), 4500);
        updateArStatus();
      } else if (!ar.onsite && wasOnsite) { arRecenter(); updateArStatus(); }
      if (!ar.onsite && !wasOnsite && !ar.previewToasted) { ar.previewToasted = true; toast(tr('toastPreview')); }
    }, () => {}, { enableHighAccuracy: true, maximumAge: 2000, timeout: 15000 });
  }
}

function exitAR() {
  window.removeEventListener('deviceorientationabsolute', onOrient);
  window.removeEventListener('deviceorientation', onOrient);
  if (ar.geoWatch != null) navigator.geolocation.clearWatch(ar.geoWatch);
  ar.geoWatch = null; ar.onsite = false; ar.previewToasted = false;
  ar.stream?.getTracks().forEach((t) => t.stop());
  ar.stream = null;
  $('camera').srcObject = null;
  state.mode = 'orbit';
  state.ghost = false; $('btnGhost').classList.remove('on');
  document.body.classList.remove('ar');
  setModeButtons();
  $('arHint').hidden = true;
  sky.visible = true; ground.visible = true;
  scene.fog = new THREE.Fog(FOG_COLOR, 90, 320);
  arWorld.rotation.set(0, 0, 0);
  site.position.set(0, 0, 0); site.rotation.set(0, 0, 0); site.scale.setScalar(1);
  if (ar.saved) { camera.position.copy(ar.saved.pos); controls.target.copy(ar.saved.target); camera.fov = ar.saved.fov; }
  camera.updateProjectionMatrix();
  controls.enabled = true;
  controls.update();
  setTime(state.t);
}

function setModeButtons() {
  $('modeOrbit').classList.toggle('active', state.mode === 'orbit');
  $('modeAR').classList.toggle('active', state.mode === 'ar');
  $('modeOrbit').setAttribute('aria-selected', state.mode === 'orbit');
  $('modeAR').setAttribute('aria-selected', state.mode === 'ar');
}
$('modeOrbit').addEventListener('click', () => { if (state.mode === 'ar') exitAR(); });
$('modeAR').addEventListener('click', () => { if (state.mode !== 'ar') enterAR(); });
$('btnRecenter').addEventListener('click', arRecenter);
$('btnGhost').addEventListener('click', () => {
  state.ghost = !state.ghost;
  $('btnGhost').classList.toggle('on', state.ghost);
  setTime(state.t);
});

// AR gestures: one-finger drag = align (or look, without a gyro); pinch / wheel = scale
const pointers = new Map();
let pinch0 = 0, scale0 = 1;
renderer.domElement.addEventListener('pointerdown', (e) => {
  if (state.mode !== 'ar') return;
  renderer.domElement.setPointerCapture(e.pointerId);
  pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
  if (pointers.size === 2) {
    const [a, b] = [...pointers.values()];
    pinch0 = Math.hypot(a.x - b.x, a.y - b.y); scale0 = ar.scale;
  }
});
renderer.domElement.addEventListener('pointermove', (e) => {
  if (state.mode !== 'ar' || !pointers.has(e.pointerId)) return;
  const prev = pointers.get(e.pointerId);
  const dx = e.clientX - prev.x, dy = e.clientY - prev.y;
  pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
  if (pointers.size === 2 && !ar.onsite) {
    const [a, b] = [...pointers.values()];
    const d = Math.hypot(a.x - b.x, a.y - b.y);
    setArScale(scale0 * d / Math.max(pinch0, 1));
  } else if (pointers.size === 1) {
    if (!ar.hasGyro) {
      ar.lookYaw -= dx * 0.004;
      ar.lookPitch = THREE.MathUtils.clamp(ar.lookPitch - dy * 0.004, -1.2, 1.2);
    } else if (ar.onsite) {
      arWorld.rotation.y += dx * 0.003;      // heading correction around the visitor
    } else {
      site.rotation.y += dx * 0.006;          // spin the model in preview
    }
  }
});
const endPointer = (e) => { pointers.delete(e.pointerId); };
renderer.domElement.addEventListener('pointerup', endPointer);
renderer.domElement.addEventListener('pointercancel', endPointer);
renderer.domElement.addEventListener('wheel', (e) => {
  if (state.mode !== 'ar' || ar.onsite) return;
  setArScale(ar.scale * Math.exp(-e.deltaY * 0.001));
}, { passive: true });

function setArScale(s) {
  const prev = ar.scale;
  ar.scale = THREE.MathUtils.clamp(s, 0.02, 1.5);
  // keep the model in front of the visitor while scaling
  const fwd = new THREE.Vector3().subVectors(site.position, camera.position).setY(0);
  const d = fwd.length();
  if (d > 1e-3) {
    fwd.normalize();
    const nd = 4 + (d - 4) * (ar.scale / prev);
    site.position.copy(camera.position).addScaledVector(fwd, Math.max(nd, 1.2));
    site.position.y = ar.scale < 0.3 ? EYE - 1.0 : 0;
  }
  site.scale.setScalar(ar.scale);
}

function stepAR() {
  if (state.mode !== 'ar') return;
  if (ar.hasGyro) applyDeviceOrientation();
  else camera.quaternion.setFromEuler(new THREE.Euler(ar.lookPitch, ar.lookYaw, 0, 'YXZ'));
  if (ar.onsite) {
    ar.userENU.lerp(ar.targetENU, 0.05);         // smooth GPS jitter
    site.position.set(-ar.userENU.x, 0, -ar.userENU.z);
  }
}

/* ------------------------------------------------------------------ */
/* Snap tourist photo                                                 */
/* ------------------------------------------------------------------ */
function drawWatermark(ctx, W, H) {
  const u = Math.max(W, H) / 1600;           // UI unit relative to a 1600-px image
  const band = Math.round(110 * u);
  const grad = ctx.createLinearGradient(0, H - band * 1.8, 0, H);
  grad.addColorStop(0, 'rgba(10,8,6,0)');
  grad.addColorStop(1, 'rgba(10,8,6,0.82)');
  ctx.fillStyle = grad;
  ctx.fillRect(0, H - band * 1.8, W, band * 1.8);

  // KPITB badge
  const bx = 34 * u, bh = 54 * u, by = H - 34 * u - bh, bw = 92 * u;
  const bg = ctx.createLinearGradient(bx, by, bx + bw, by + bh);
  bg.addColorStop(0, '#18a08d'); bg.addColorStop(1, '#0f6f8f');
  ctx.fillStyle = bg;
  ctx.beginPath(); ctx.roundRect(bx, by, bw, bh, 12 * u); ctx.fill();
  ctx.fillStyle = '#fff';
  ctx.font = `800 ${24 * u}px Inter, system-ui, sans-serif`;
  ctx.textBaseline = 'middle';
  ctx.textAlign = 'center';
  ctx.fillText('KPITB', bx + bw / 2, by + bh / 2 + 1 * u);

  // Text
  ctx.textAlign = 'left';
  const tx = bx + bw + 18 * u;
  ctx.fillStyle = '#ffffff';
  ctx.font = `700 ${30 * u}px Inter, system-ui, sans-serif`;
  ctx.fillText('Takht-i-Bahi AI Digital Twin | KPITB 2026', tx, by + 16 * u);
  ctx.fillStyle = '#f6d58f';
  ctx.font = `500 ${19 * u}px Inter, system-ui, sans-serif`;
  const era = state.t < 0.03 ? '2026 CE · Ruins' : state.t > 0.97 ? 'c. 150 CE · Kushan Gandhara' : `Time-Warp ${Math.round(state.t * 100)}% · c. ${Math.round(2026 - state.t * 1876)} CE`;
  ctx.fillText(`${era}  ·  UNESCO World Heritage · Mardan, Khyber Pakhtunkhwa`, tx, by + 44 * u);

  // Date stamp, right aligned
  ctx.textAlign = 'right';
  ctx.fillStyle = 'rgba(255,255,255,0.75)';
  ctx.font = `500 ${17 * u}px Inter, system-ui, sans-serif`;
  ctx.fillText(new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }), W - 34 * u, by + 44 * u);

  // thin gold frame
  ctx.strokeStyle = 'rgba(231,182,92,0.85)';
  ctx.lineWidth = Math.max(2, 3 * u);
  ctx.strokeRect(14 * u, 14 * u, W - 28 * u, H - 28 * u);
}

let lastPhotoURL = null, lastPhotoBlob = null;
async function snapPhoto() {
  const flash = document.createElement('div');
  flash.className = 'flash';
  document.body.appendChild(flash);
  setTimeout(() => flash.remove(), 500);

  // Render one frame at high resolution (long edge ≈ 3000 px)
  const longCss = Math.max(innerWidth, innerHeight);
  const maxTex = renderer.capabilities.maxTextureSize;
  const pr = Math.min(3000 / longCss, 4, maxTex / longCss);
  pins.style.visibility = 'hidden';
  renderer.setPixelRatio(pr);
  renderer.render(scene, camera);

  const src = renderer.domElement;
  const W = src.width, H = src.height;
  const out = document.createElement('canvas');
  out.width = W; out.height = H;
  const ctx = out.getContext('2d');

  if (state.mode === 'ar') {          // camera frame underneath, cover-fit like the CSS
    const v = $('camera');
    const vw = v.videoWidth || W, vh = v.videoHeight || H;
    const s = Math.max(W / vw, H / vh);
    ctx.drawImage(v, (W - vw * s) / 2, (H - vh * s) / 2, vw * s, vh * s);
  }
  ctx.drawImage(src, 0, 0);           // same task as render() → buffer still valid

  renderer.setPixelRatio(BASE_DPR);
  renderer.setSize(innerWidth, innerHeight);
  pins.style.visibility = '';

  await document.fonts?.ready;
  drawWatermark(ctx, W, H);

  const blob = await new Promise((r) => out.toBlob(r, 'image/jpeg', 0.92));
  if (lastPhotoURL) URL.revokeObjectURL(lastPhotoURL);
  lastPhotoURL = URL.createObjectURL(blob);
  lastPhotoBlob = blob;
  $('photoImg').src = lastPhotoURL;
  const a = $('photoDownload');
  a.href = lastPhotoURL;
  a.download = `takht-i-bahi-kpitb-2026-${Date.now()}.jpg`;
  const file = new File([blob], 'takht-i-bahi-kpitb-2026.jpg', { type: 'image/jpeg' });
  $('photoShare').hidden = !(navigator.canShare && navigator.canShare({ files: [file] }));
  $('photoModal').hidden = false;
  toast(tr('toastSaved'), 1800);
}
const pins = $('pins');
$('btnSnap').addEventListener('click', snapPhoto);
$('photoClose').addEventListener('click', () => { $('photoModal').hidden = true; });
$('photoShare').addEventListener('click', async () => {
  try {
    await navigator.share({ files: [new File([lastPhotoBlob], 'takht-i-bahi-kpitb-2026.jpg', { type: 'image/jpeg' })], title: 'Takht-i-Bahi AI Digital Twin', text: 'Takht-i-Bahi AI Digital Twin | KPITB 2026' });
  } catch { /* user cancelled */ }
});

/* ------------------------------------------------------------------ */
/* Misc UI                                                            */
/* ------------------------------------------------------------------ */
$('btnFull').addEventListener('click', () => {
  const d = document, el = d.documentElement;
  if (d.fullscreenElement || d.webkitFullscreenElement) (d.exitFullscreen || d.webkitExitFullscreen).call(d);
  else if (el.requestFullscreen) el.requestFullscreen().catch(() => toast(tr('toastNoFs')));
  else if (el.webkitRequestFullscreen) el.webkitRequestFullscreen();
  else toast(tr('toastNoFs'));
});
$('btnAbout').addEventListener('click', () => { $('aboutModal').hidden = false; });
$('aboutClose').addEventListener('click', () => { $('aboutModal').hidden = true; });
for (const id of ['photoModal', 'aboutModal']) $(id).addEventListener('click', (e) => { if (e.target.id === id) $(id).hidden = true; });
addEventListener('keydown', (e) => {
  if (e.key === 'Escape') { $('photoModal').hidden = true; $('aboutModal').hidden = true; closeCard(); }
});

addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});

/* ------------------------------------------------------------------ */
/* Loop                                                               */
/* ------------------------------------------------------------------ */
renderer.setAnimationLoop((now) => {
  stepPlay(now);
  if (state.mode === 'orbit') { stepFly(now); controls.update(); }
  else stepAR();
  if (ruins) updatePins();
  for (const a of Object.values(anchors)) a.material.opacity = 0.65 + 0.35 * Math.sin(now * 0.004);
  renderer.render(scene, camera);
});

setLang('en');
init();

// expose for debugging in the console
window.__twin = { scene, camera, setTime, state };
