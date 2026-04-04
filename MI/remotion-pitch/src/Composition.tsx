import React from "react";
import { AbsoluteFill, Sequence } from "remotion";

// Core Slides
import TitleSlide from "./slides/TitleSlide";
import TeamSlide from "./slides/TeamSlide";
import AgendaSlide from "./slides/AgendaSlide";
import ElevatorPitchSlide from "./slides/ElevatorPitchSlide";

// Problem & Market
import ProblemSlide from "./slides/ProblemSlide";
import StakeholdersSlide from "./slides/StakeholdersSlide";
import BenchmarkingSlide from "./slides/BenchmarkingSlide";
import CompetitiveLandscapeSlide from "./slides/CompetitiveLandscapeSlide";

// Solution & Technical
import SolutionOverviewSlide from "./slides/SolutionOverviewSlide";
import SystemFlowSlide from "./slides/SystemFlowSlide";
import TechnicalArchitectureSlide from "./slides/TechnicalArchitectureSlide";
import OBUDetailSlide from "./slides/OBUDetailSlide";
import RSUDetailSlide from "./slides/RSUDetailSlide";

// Business & Financial
import GoToMarketSlide from "./slides/GoToMarketSlide";
import UnitEconomicsSlide from "./slides/UnitEconomicsSlide";
import FinancialProjectionsSlide from "./slides/FinancialProjectionsSlide";
import PricingModelSlide from "./slides/PricingModelSlide";
import ExitStrategySlide from "./slides/ExitStrategySlide";

// Conclusion & Appendix
import ConclusionSlide from "./slides/ConclusionSlide";
import FundingAskSlide from "./slides/FundingAskSlide";
import AppendixCostSlide from "./slides/AppendixCostSlide";
import AppendixCloudSlide from "./slides/AppendixCloudSlide";
import AppendixRevenueSlide from "./slides/AppendixRevenueSlide";
import AppendixDatabaseSlide from "./slides/AppendixDatabaseSlide";

const SLIDE_DURATION = 30 * 15; // 15 seconds per slide at 30fps

const slides = [
  // Act 1: Opening (0-3)
  { component: TitleSlide, name: "Title" },
  { component: TeamSlide, name: "Team" },
  { component: AgendaSlide, name: "Agenda" },
  { component: ElevatorPitchSlide, name: "Elevator Pitch" },

  // Act 2: Problem & Market (4-7)
  { component: ProblemSlide, name: "Problem Statement" },
  { component: StakeholdersSlide, name: "Stakeholders" },
  { component: BenchmarkingSlide, name: "Market Assessment" },
  { component: CompetitiveLandscapeSlide, name: "Competitive Landscape" },

  // Act 3: Solution & Technical (8-12)
  { component: SolutionOverviewSlide, name: "Solution Overview" },
  { component: SystemFlowSlide, name: "System Flow" },
  { component: TechnicalArchitectureSlide, name: "Technical Architecture" },
  { component: OBUDetailSlide, name: "OBU Detail" },
  { component: RSUDetailSlide, name: "RSU Detail" },

  // Act 4: Business (13-17)
  { component: GoToMarketSlide, name: "Go-to-Market" },
  { component: UnitEconomicsSlide, name: "Unit Economics" },
  { component: FinancialProjectionsSlide, name: "Financial Projections" },
  { component: PricingModelSlide, name: "Pricing Model" },
  { component: ExitStrategySlide, name: "Exit Strategy" },

  // Act 5: Conclusion (18-19)
  { component: ConclusionSlide, name: "Conclusion" },
  { component: FundingAskSlide, name: "Funding Ask" },

  // Appendix (20-23)
  { component: AppendixCostSlide, name: "Appendix: Costs" },
  { component: AppendixCloudSlide, name: "Appendix: Cloud" },
  { component: AppendixRevenueSlide, name: "Appendix: Revenue" },
  { component: AppendixDatabaseSlide, name: "Appendix: Database" },
];

export const AutoParkPitchDeck: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#0A1628" }}>
      {slides.map((slide, index) => (
        <Sequence
          key={slide.name}
          from={index * SLIDE_DURATION}
          durationInFrames={SLIDE_DURATION}
          name={slide.name}
        >
          <slide.component />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
