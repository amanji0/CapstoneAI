"use client";

import { useState, useEffect, createContext, useContext } from "react";

// ─── Theme Context ───────────────────────────────────────────────────────
const ThemeContext = createContext({ theme: "dark", toggle: () => {} });

function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState("dark");

  useEffect(() => {
    const saved = localStorage.getItem("capstone-theme");
    if (saved) setTheme(saved);
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
    localStorage.setItem("capstone-theme", theme);
  }, [theme]);

  const toggle = () => setTheme((t) => (t === "dark" ? "light" : "dark"));

  return (
    <ThemeContext.Provider value={{ theme, toggle }}>
      <div className={theme === "dark" ? "bg-[#0a0a0a] text-white" : "bg-white text-gray-900"} style={{ minHeight: "100vh", transition: "background-color 0.3s, color 0.3s" }}>
        {children}
      </div>
    </ThemeContext.Provider>
  );
}

function useTheme() {
  return useContext(ThemeContext);
}

// ─── Navbar ──────────────────────────────────────────────────────────────
function Navbar({ onHome }: { onHome: () => void }) {
  const { theme, toggle } = useTheme();
  const d = theme === "dark";

  return (
    <nav className={`sticky top-0 z-50 backdrop-blur-xl border-b ${d ? "bg-[#0a0a0a]/80 border-white/[0.06]" : "bg-white/80 border-gray-200"}`} style={{ transition: "all 0.3s" }}>
      <div className="max-w-4xl mx-auto px-6 h-14 flex items-center justify-between">
        <button onClick={onHome} className="flex items-center gap-2 group">
          <span className="text-lg font-bold tracking-tight">
            Capstone<span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-500 to-blue-500">AI</span>
          </span>
        </button>

        <button
          onClick={toggle}
          className={`w-9 h-9 rounded-full flex items-center justify-center border transition-all ${d ? "bg-white/5 border-white/10 hover:bg-white/10 text-white" : "bg-gray-100 border-gray-200 hover:bg-gray-200 text-gray-700"}`}
          title={`Switch to ${d ? "light" : "dark"} mode`}
        >
          {d ? (
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" strokeWidth="2" strokeLinecap="round"/></svg>
          ) : (
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
          )}
        </button>
      </div>
    </nav>
  );
}

// ─── Data ────────────────────────────────────────────────────────────────
const SKILL_OPTIONS = [
  "Python", "JavaScript", "TypeScript", "React", "Next.js", "Node.js",
  "Flask", "Django", "FastAPI", "MongoDB", "PostgreSQL", "MySQL",
  "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
  "Docker", "AWS", "Firebase", "TensorFlow", "PyTorch", "React Native",
  "Flutter", "Tailwind CSS", "GraphQL", "Redis", "Kubernetes",
];

const INTEREST_OPTIONS = [
  "Healthcare", "Education", "Finance", "Agriculture", "E-Commerce",
  "Social Media", "Climate & Environment", "Cybersecurity", "Gaming",
  "Transportation", "Food & Nutrition", "Mental Health", "Music & Art",
  "Legal Tech", "Real Estate", "Sports & Fitness", "Accessibility",
];

type ProjectIdea = {
  title: string;
  tagline: string;
  domain: string;
  matching_skills?: string[];
  estimated_weeks?: number;
};

type GitHubRepo = {
  name: string;
  description: string;
  language: string;
  stars: number;
  forks: number;
  url: string;
};

type GitHubAnalysis = {
  username: string;
  total_repos: number;
  total_stars: number;
  top_languages: string[];
  estimated_level: string;
  level_reason: string;
  top_repos: GitHubRepo[];
};

// ─── Main App ────────────────────────────────────────────────────────────
function AppContent() {
  const { theme } = useTheme();
  const d = theme === "dark";

  const [step, setStep] = useState(0);
  const [name, setName] = useState("");
  const [field, setField] = useState("");
  const [complexity, setComplexity] = useState("");
  const [timeAvailable, setTimeAvailable] = useState(16);
  const [selectedSkills, setSelectedSkills] = useState<string[]>([]);
  const [selectedInterests, setSelectedInterests] = useState<string[]>([]);
  const [ideas, setIdeas] = useState<ProjectIdea[]>([]);
  const [loading, setLoading] = useState(false);

  const [githubUsername, setGithubUsername] = useState("");
  const [githubAnalysis, setGithubAnalysis] = useState<GitHubAnalysis | null>(null);
  const [githubLoading, setGithubLoading] = useState(false);
  const [githubError, setGithubError] = useState("");

  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

  const toggleItem = (item: string, list: string[], setList: (v: string[]) => void) => {
    setList(list.includes(item) ? list.filter((i) => i !== item) : [...list, item]);
  };

  const analyzeGitHub = async () => {
    if (!githubUsername.trim()) return;
    setGithubLoading(true);
    setGithubError("");
    setGithubAnalysis(null);
    try {
      const res = await fetch(`${API_URL}/api/analyze-github`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: githubUsername.trim() }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Failed to analyze.");
      }
      const data: GitHubAnalysis = await res.json();
      setGithubAnalysis(data);
      if (data.estimated_level) setComplexity(data.estimated_level);
      const languageToSkill: Record<string, string> = {
        Python: "Python", JavaScript: "JavaScript", TypeScript: "TypeScript",
        HTML: "React", Dart: "Flutter", CSS: "Tailwind CSS",
      };
      const detectedSkills = data.top_languages
        .map((l) => languageToSkill[l.replace(" ", "_")] || l)
        .filter((s) => SKILL_OPTIONS.includes(s));
      if (detectedSkills.length > 0) {
        setSelectedSkills((prev) => Array.from(new Set([...prev, ...detectedSkills])));
      }
    } catch (err: unknown) {
      setGithubError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setGithubLoading(false);
    }
  };

  const generateIdeas = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/generate-ideas`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name, academic_field: field, interests: selectedInterests,
          skills: selectedSkills, complexity, time_available: timeAvailable,
          github_username: githubUsername || null,
        }),
      });
      const data = await response.json();
      if (data.ideas) { setIdeas(data.ideas); setStep(2); }
    } catch {
      alert("Could not connect to backend. Make sure FastAPI is running on port 8000.");
    } finally {
      setLoading(false);
    }
  };

  // ── Styles ──
  const card = d ? "bg-white/[0.03] border-white/[0.06] hover:border-white/[0.12]" : "bg-gray-50 border-gray-200 hover:border-gray-300";
  const input = d ? "bg-white/5 border-white/10 text-white placeholder:text-neutral-600 focus:ring-violet-500/50 focus:border-violet-500/50" : "bg-white border-gray-300 text-gray-900 placeholder:text-gray-400 focus:ring-violet-500/50 focus:border-violet-500/50";
  const label = d ? "text-neutral-300" : "text-gray-700";
  const subtitle = d ? "text-neutral-400" : "text-gray-500";
  const chipOff = d ? "bg-white/5 border-white/10 text-neutral-500 hover:text-neutral-300 hover:border-white/20" : "bg-gray-100 border-gray-200 text-gray-500 hover:text-gray-700 hover:border-gray-300";
  const chipOnViolet = "bg-violet-500/20 border-violet-500/50 text-violet-400";
  const chipOnBlue = "bg-blue-500/20 border-blue-500/50 text-blue-400";
  const backBtn = d ? "text-neutral-500 hover:text-white" : "text-gray-400 hover:text-gray-900";

  // ─── Landing ───
  if (step === 0) {
    return (
      <>
        <Navbar onHome={() => setStep(0)} />
        <div className="flex flex-col items-center justify-center px-6" style={{ minHeight: "calc(100vh - 56px)" }}>
          <div className="max-w-xl w-full text-center">
            <div className={`inline-flex items-center gap-2 rounded-full px-4 py-1.5 text-sm mb-8 border ${d ? "bg-white/5 border-white/10 text-neutral-400" : "bg-gray-100 border-gray-200 text-gray-500"}`}>
              <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
              Powered by AI
            </div>

            <h1 className="text-5xl sm:text-6xl font-bold tracking-tight leading-[1.1] mb-6">
              Capstone<span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-500 to-blue-500">AI</span>
            </h1>

            <p className={`text-lg leading-relaxed mb-10 max-w-md mx-auto ${subtitle}`}>
              Stop guessing. Generate a complete, award-winning final-year project
              blueprint — tailored to your skills.
            </p>

            <button
              onClick={() => setStep(1)}
              className={`font-medium px-8 py-3 rounded-full transition-colors text-sm ${d ? "bg-white text-black hover:bg-neutral-200" : "bg-gray-900 text-white hover:bg-gray-800"}`}
            >
              Get Started →
            </button>

            <p className={`text-xs mt-6 ${d ? "text-neutral-600" : "text-gray-400"}`}>
              Free to use · No account required · Takes 2 minutes
            </p>
          </div>
        </div>
      </>
    );
  }

  // ─── Form ───
  if (step === 1) {
    return (
      <>
        <Navbar onHome={() => setStep(0)} />
        <div className="px-6 py-12">
          <div className="max-w-2xl mx-auto">
            <button onClick={() => setStep(0)} className={`text-sm transition-colors mb-8 flex items-center gap-1 ${backBtn}`}>
              ← Back
            </button>

            <h2 className="text-3xl font-bold mb-2">Tell us about yourself</h2>
            <p className={`${subtitle} mb-10`}>We&apos;ll generate ideas matched to your profile.</p>

            {/* ── GitHub Analyzer ── */}
            <div className={`mb-10 p-6 border rounded-2xl ${card}`}>
              <div className="flex items-center gap-3 mb-4">
                <svg className={`w-5 h-5 ${subtitle}`} fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                </svg>
                <h3 className="text-lg font-semibold">Analyze Your GitHub</h3>
                <span className={`text-xs ml-auto ${d ? "text-neutral-600" : "text-gray-400"}`}>Optional</span>
              </div>
              <p className={`text-sm mb-4 ${subtitle}`}>
                Paste your GitHub profile link — we&apos;ll scan all your repos to understand your tech stack, experience level, and auto-fill your skills.
              </p>
              <div className="flex gap-3">
                <input
                  type="text"
                  value={githubUsername}
                  onChange={(e) => setGithubUsername(e.target.value)}
                  placeholder="https://github.com/your-username"
                  className={`flex-1 rounded-lg px-4 py-2.5 text-sm border focus:outline-none focus:ring-2 transition-all ${input}`}
                />
                <button
                  onClick={analyzeGitHub}
                  disabled={githubLoading || !githubUsername.trim()}
                  className={`px-5 py-2.5 rounded-lg text-sm font-medium border transition-all disabled:opacity-30 disabled:cursor-not-allowed shrink-0 ${d ? "bg-white/10 border-white/10 text-white hover:bg-white/15" : "bg-gray-900 border-gray-900 text-white hover:bg-gray-800"}`}
                >
                  {githubLoading ? (
                    <span className="flex items-center gap-2">
                      <span className={`w-3 h-3 border-2 rounded-full animate-spin ${d ? "border-white/30 border-t-white" : "border-white/30 border-t-white"}`} />
                      Scanning...
                    </span>
                  ) : "Scan Profile"}
                </button>
              </div>
              {githubError && <p className="text-red-400 text-sm mt-3">{githubError}</p>}

              {githubAnalysis && (
                <div className={`mt-5 pt-5 border-t ${d ? "border-white/[0.06]" : "border-gray-200"}`}>
                  <div className="grid grid-cols-3 gap-4 mb-4">
                    <div className="text-center">
                      <p className="text-2xl font-bold">{githubAnalysis.total_repos}</p>
                      <p className={`text-xs ${d ? "text-neutral-500" : "text-gray-500"}`}>Repos</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold">{githubAnalysis.total_stars}</p>
                      <p className={`text-xs ${d ? "text-neutral-500" : "text-gray-500"}`}>Stars</p>
                    </div>
                    <div className="text-center">
                      <p className={`text-2xl font-bold ${
                        githubAnalysis.estimated_level === "Advanced" ? "text-green-500" :
                        githubAnalysis.estimated_level === "Intermediate" ? "text-yellow-500" : "text-blue-500"
                      }`}>{githubAnalysis.estimated_level}</p>
                      <p className={`text-xs ${d ? "text-neutral-500" : "text-gray-500"}`}>Level</p>
                    </div>
                  </div>
                  <p className={`text-sm mb-3 ${subtitle}`}>{githubAnalysis.level_reason}</p>
                  <div className="flex flex-wrap gap-1.5 mb-4">
                    {githubAnalysis.top_languages.map((lang) => (
                      <span key={lang} className="px-2.5 py-1 rounded-full text-xs font-medium bg-green-500/10 text-green-500 border border-green-500/20">
                        {lang}
                      </span>
                    ))}
                  </div>
                  <div className="space-y-2">
                    {githubAnalysis.top_repos.slice(0, 4).map((repo) => (
                      <a key={repo.name} href={repo.url} target="_blank" rel="noopener noreferrer"
                        className={`flex items-center justify-between p-3 rounded-lg transition-colors group ${d ? "bg-white/[0.03] hover:bg-white/[0.06]" : "bg-white hover:bg-gray-100"}`}
                      >
                        <div className="min-w-0">
                          <p className="text-sm font-medium truncate group-hover:text-violet-500 transition-colors">{repo.name}</p>
                          <p className={`text-xs truncate ${d ? "text-neutral-500" : "text-gray-500"}`}>{repo.description}</p>
                        </div>
                        <div className="flex items-center gap-3 shrink-0 ml-4">
                          {repo.language && <span className={`text-xs ${d ? "text-neutral-500" : "text-gray-400"}`}>{repo.language}</span>}
                          {repo.stars > 0 && <span className={`text-xs ${d ? "text-neutral-500" : "text-gray-400"}`}>⭐ {repo.stars}</span>}
                        </div>
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Name */}
            <div className="mb-8">
              <label className={`block text-sm font-medium mb-2 ${label}`}>Your Name</label>
              <input type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Aman"
                className={`w-full rounded-lg px-4 py-3 border focus:outline-none focus:ring-2 transition-all ${input}`}
              />
            </div>

            {/* Field */}
            <div className="mb-8">
              <label className={`block text-sm font-medium mb-2 ${label}`}>Academic Field</label>
              <select value={field} onChange={(e) => setField(e.target.value)}
                className={`w-full rounded-lg px-4 py-3 border focus:outline-none focus:ring-2 transition-all appearance-none ${input}`}
              >
                <option value="" className={d ? "bg-neutral-900" : ""}>Select your field</option>
                <option value="Computer Science" className={d ? "bg-neutral-900" : ""}>Computer Science</option>
                <option value="Information Technology" className={d ? "bg-neutral-900" : ""}>Information Technology</option>
                <option value="Data Science" className={d ? "bg-neutral-900" : ""}>Data Science</option>
                <option value="Software Engineering" className={d ? "bg-neutral-900" : ""}>Software Engineering</option>
                <option value="AI & ML" className={d ? "bg-neutral-900" : ""}>AI & Machine Learning</option>
                <option value="Cybersecurity" className={d ? "bg-neutral-900" : ""}>Cybersecurity</option>
              </select>
            </div>

            {/* Complexity */}
            <div className="mb-8">
              <label className={`block text-sm font-medium mb-2 ${label}`}>
                Complexity Level
                {githubAnalysis && <span className="text-green-500 text-xs ml-2">(auto-detected from GitHub)</span>}
              </label>
              <div className="grid grid-cols-3 gap-3">
                {["Beginner", "Intermediate", "Advanced"].map((level) => (
                  <button key={level} onClick={() => setComplexity(level)}
                    className={`py-3 rounded-lg border text-sm font-medium transition-all ${
                      complexity === level ? chipOnViolet : chipOff
                    }`}
                  >{level}</button>
                ))}
              </div>
            </div>

            {/* Time */}
            <div className="mb-8">
              <label className={`block text-sm font-medium mb-2 ${label}`}>
                Time Available: <span className="text-violet-500">{timeAvailable} weeks</span>
              </label>
              <input type="range" min={4} max={24} value={timeAvailable}
                onChange={(e) => setTimeAvailable(Number(e.target.value))} className="w-full accent-violet-500"
              />
              <div className={`flex justify-between text-xs mt-1 ${d ? "text-neutral-600" : "text-gray-400"}`}>
                <span>4 weeks</span><span>24 weeks</span>
              </div>
            </div>

            {/* Skills */}
            <div className="mb-8">
              <label className={`block text-sm font-medium mb-3 ${label}`}>
                Your Skills <span className={d ? "text-neutral-600" : "text-gray-400"}>({selectedSkills.length} selected)</span>
                {githubAnalysis && selectedSkills.length > 0 && <span className="text-green-500 text-xs ml-2">✓ auto-filled from GitHub</span>}
              </label>
              <div className="flex flex-wrap gap-2">
                {SKILL_OPTIONS.map((skill) => (
                  <button key={skill} onClick={() => toggleItem(skill, selectedSkills, setSelectedSkills)}
                    className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-all ${selectedSkills.includes(skill) ? chipOnViolet : chipOff}`}
                  >{skill}</button>
                ))}
              </div>
            </div>

            {/* Interests */}
            <div className="mb-10">
              <label className={`block text-sm font-medium mb-3 ${label}`}>
                Your Interests <span className={d ? "text-neutral-600" : "text-gray-400"}>({selectedInterests.length} selected)</span>
              </label>
              <div className="flex flex-wrap gap-2">
                {INTEREST_OPTIONS.map((interest) => (
                  <button key={interest} onClick={() => toggleItem(interest, selectedInterests, setSelectedInterests)}
                    className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-all ${selectedInterests.includes(interest) ? chipOnBlue : chipOff}`}
                  >{interest}</button>
                ))}
              </div>
            </div>

            {/* Submit */}
            <button onClick={generateIdeas}
              disabled={loading || !name || !field || !complexity || selectedSkills.length === 0}
              className={`w-full font-medium py-3.5 rounded-full transition-colors disabled:opacity-30 disabled:cursor-not-allowed text-sm ${d ? "bg-white text-black hover:bg-neutral-200" : "bg-gray-900 text-white hover:bg-gray-800"}`}
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <span className={`w-4 h-4 border-2 rounded-full animate-spin ${d ? "border-black/30 border-t-black" : "border-white/30 border-t-white"}`} />
                  Generating Ideas...
                </span>
              ) : "Generate Project Ideas →"}
            </button>
          </div>
        </div>
      </>
    );
  }

  // ─── Results ───
  return (
    <>
      <Navbar onHome={() => setStep(0)} />
      <div className="px-6 py-12">
        <div className="max-w-3xl mx-auto">
          <button onClick={() => { setStep(1); setIdeas([]); }} className={`text-sm transition-colors mb-8 flex items-center gap-1 ${backBtn}`}>
            ← Edit Profile & Regenerate
          </button>

          <h2 className="text-3xl font-bold mb-2">Your Project Ideas</h2>
          <p className={`${subtitle} mb-10`}>
            Here are {ideas.length} ideas tailored for you, {name}. Change your skills or interests and regenerate for different results.
          </p>

          <div className="space-y-4">
            {ideas.map((idea, index) => (
              <div key={index} className={`group p-6 border rounded-2xl transition-all ${card}`}>
                <div className="flex items-start justify-between gap-4 mb-3">
                  <h3 className="text-xl font-semibold">{idea.title}</h3>
                  <span className="shrink-0 text-[11px] font-medium px-2.5 py-1 rounded-full bg-violet-500/10 text-violet-500 border border-violet-500/20">
                    {idea.domain}
                  </span>
                </div>
                <p className={`text-sm leading-relaxed mb-4 ${subtitle}`}>{idea.tagline}</p>
                <div className="flex flex-wrap items-center gap-2 mb-5">
                  {idea.matching_skills?.map((skill) => (
                    <span key={skill} className="text-[11px] px-2 py-0.5 rounded-full bg-green-500/10 text-green-500 border border-green-500/20">{skill}</span>
                  ))}
                  {idea.estimated_weeks && (
                    <span className="text-[11px] px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-500 border border-blue-500/20">~{idea.estimated_weeks} weeks</span>
                  )}
                </div>
                <button className={`text-sm font-medium transition-colors flex items-center gap-1.5 group-hover:gap-2.5 ${d ? "text-white/60 hover:text-white" : "text-gray-400 hover:text-gray-900"}`}>
                  Generate Full Blueprint <span className="transition-all">→</span>
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}

export default function Home() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
}
