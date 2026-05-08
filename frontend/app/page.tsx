import AvatarStage from "../components/AvatarStage";
import EmotionPanel from "../components/EmotionPanel";
import ModeSwitcher from "../components/ModeSwitcher";

export default function HomePage() {
  return (
    <main className="mx-auto grid max-w-5xl gap-4 p-6">
      <h1 className="text-2xl font-bold">AvatarLM Control Deck</h1>
      <p className="text-gray-700">
        AI performs knowledge with emotion, presence, and environment.
      </p>
      <ModeSwitcher
        modes={["video_explainer", "podcast", "infographic", "quiz"]}
        selectedMode="video_explainer"
      />
      <EmotionPanel selectedEmotion="heartbroken" emotions={["heartbroken", "confident"]} />
      <AvatarStage scene="cliff" emotion="heartbroken" mode="video_explainer" />
    </main>
  );
}

