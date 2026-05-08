type EmotionPanelProps = {
  selectedEmotion: string;
  emotions: string[];
};

export default function EmotionPanel({ selectedEmotion, emotions }: EmotionPanelProps) {
  return (
    <section className="rounded-xl border p-4 shadow-sm">
      <h2 className="text-lg font-semibold">Emotion Presets</h2>
      <ul className="list-inside list-disc">
        {emotions.map((emotion) => (
          <li key={emotion}>
            {emotion}
            {emotion === selectedEmotion ? " (active)" : ""}
          </li>
        ))}
      </ul>
    </section>
  );
}

