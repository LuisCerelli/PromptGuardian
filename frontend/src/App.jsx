import { useState } from "react";
import SignInSide from "../sign-in-side/SignInSide.jsx";
import About from "../sign-in-side/About.jsx";
import { Routes, Route } from "react-router-dom";

function App() {
  const [generatedPrompt, setGeneratedPrompt] = useState("");

  return (
    <div className="min-h-screen flex items-center justify-center transition-all duration-500">
      <div className="w-full max-w-2xl p-6">
        <Routes>
          <Route
            path="/"
            element={
              <SignInSide
                generatedPrompt={generatedPrompt}
                setGeneratedPrompt={setGeneratedPrompt}
              />
            }
          />
          <Route path="/about" element={<About />} />
        </Routes>
      </div>
    </div>
  );
}

export default App;
