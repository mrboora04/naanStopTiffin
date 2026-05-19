"use client";

export default function LikeDislikeBar({
  likes,
  dislikes,
}: {
  likes: number;
  dislikes: number;
}) {
  const total = likes + dislikes;
  const likePercent = total > 0 ? (likes / total) * 100 : 50;

  return (
    <div className="flex items-center gap-3 w-full">
      <span className="text-base text-green-600 min-w-[32px]">👍 {likes}</span>
      <div className="flex-1 h-3 bg-red-200 rounded-full overflow-hidden">
        <div
          className="h-full bg-green-500 rounded-full transition-all"
          style={{ width: `${likePercent}%` }}
        />
      </div>
      <span className="text-base text-red-500 min-w-[32px]">👎 {dislikes}</span>
    </div>
  );
}
