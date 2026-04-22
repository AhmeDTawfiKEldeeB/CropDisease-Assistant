export const imageUrls = {
  hero: "https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?auto=format&fit=crop&w=1200&q=80",
  leaf: "https://images.unsplash.com/photo-1459156212016-c812468e2115?auto=format&fit=crop&w=1400&q=80",
  greenhouse:
    "https://images.unsplash.com/photo-1586771107445-d3ca888129ff?auto=format&fit=crop&w=1200&q=80",
  topPlants:
    "https://images.unsplash.com/photo-1466692476868-aef1dfb1e735?auto=format&fit=crop&w=1300&q=80",
};

export const historyItems = [
  { id: "DG-1001", plant: "Tomato", disease: "Early Blight", confidence: 94, date: "2026-04-12", severity: "high" },
  { id: "DG-1002", plant: "Cucumber", disease: "Powdery Mildew", confidence: 88, date: "2026-04-11", severity: "medium" },
  { id: "DG-1003", plant: "Pepper", disease: "Healthy", confidence: 99, date: "2026-04-09", severity: "low" },
  { id: "DG-1004", plant: "Basil", disease: "Leaf Spot", confidence: 81, date: "2026-04-06", severity: "medium" },
];

export const chatMessages = [
  {
    id: 1,
    role: "ai",
    time: "10:24 AM",
    text: "Hello! I reviewed your tomato scan. The pattern strongly indicates Early Blight (Alternaria solani).",
  },
  {
    id: 2,
    role: "user",
    time: "10:25 AM",
    text: "How fast can this spread? I have 20 plants nearby.",
  },
  {
    id: 3,
    role: "ai",
    time: "10:26 AM",
    text: "It spreads rapidly in high humidity above 80%, especially with leaf wetness and splash irrigation.",
    warning:
      "If untreated, severe defoliation can happen within 2-3 weeks and reduce yield significantly.",
    bullets: [
      "Prune infected lower leaves immediately.",
      "Improve airflow and maintain humidity below 65%.",
      "Apply a copper-based fungicide as directed.",
    ],
  },
];