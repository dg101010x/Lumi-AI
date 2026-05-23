export type Mobility = "independent" | "walker" | "wheelchair" | "bed";

export type Caregiver = {
  name?: string;
  email?: string;
  phone?: string;
};

export type Resident = {
  name?: string;
  nickname?: string;
  dob?: string;
  photoUrl?: string;
  room?: string;
};

export type Health = {
  conditions: string[];
  mobility?: Mobility;
};

export type Likes = {
  music?: string;
  food?: string;
  hobbies?: string;
  family?: string;
};

export type FamilyMember = {
  name?: string;
  phone: string;
  relationship?: string;
};

export type AlertPrefs = {
  emergencySms: boolean;
  emergencyPush: boolean;
  medsReminders: boolean;
  quietHoursStart?: string;
  quietHoursEnd?: string;
};

export type OnboardingState = {
  caregiver: Caregiver;
  resident: Resident;
  health: Health;
  likes: Likes;
  family: FamilyMember[];
  alerts: AlertPrefs;
  completedAt?: string;
};

export const emptyOnboardingState: OnboardingState = {
  caregiver: {},
  resident: {},
  health: { conditions: [] },
  likes: {},
  family: [],
  alerts: {
    emergencySms: true,
    emergencyPush: true,
    medsReminders: true,
  },
};
