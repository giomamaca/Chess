export type Screen =
  | "registration"
  | "menu"
  | "offline-setup"
  | "online-setup"
  | "online-private"
  | "online-quick-match"
  | "online-join-private-match"
  | "online-waiting-room"
  | "online-private-created"
  | "game-offline"
  | "game-online";

export type Piece = {
  name: string;
  x: number;
  y: number;
  image: string;
};

export type Move = { x: number; y: number };

export type PromotionOffer = { name: string; image: string };
export type PromotionData = { x: number; y: number; color: string; offers: PromotionOffer[] };