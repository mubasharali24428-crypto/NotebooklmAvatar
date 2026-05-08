type AvatarStageProps = {
  scene: string;
  emotion: string;
  mode: "video_explainer" | "podcast" | "infographic" | "quiz";
};

export default function AvatarStage({ scene, emotion, mode }: AvatarStageProps) {
  return (
    <section className="rounded-xl border p-4 shadow-sm">
      <h2 className="text-lg font-semibold">Avatar Stage</h2>
      <p>Scene: {scene}</p>
      <p>Emotion: {emotion}</p>
      <p>Mode: {mode}</p>
      <p className="text-sm text-gray-600">
        Rendering pipeline target: Three.js avatar + motion states (idle/speaking/walking/reacting).
      </p>
    </section>
  );
}

