import React from 'react';

export default function DisclaimerBanner({ text }) {
  const defaultText =
    "Advisory & Uncertainty Notice: Admission likelihood ranges and recommendations are probabilistic estimates computed from historical cutoff benchmarks. They do not constitute an admission or placement guarantee. Always verify with official seat allocation authority (e.g. JoSAA/CSAB/State Authority).";

  return (
    <aside aria-label="Advisory Notice" className="disclaimer-banner">
      <span className="disclaimer-icon" aria-hidden="true">&#9888;</span>
      <span>{text || defaultText}</span>
    </aside>
  );
}
