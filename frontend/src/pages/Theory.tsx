import katex from "katex";
import "katex/dist/katex.min.css";

// Display and inline maths (KaTeX renders to HTML; no script runs at view time)
function Eq({ tex }: { tex: string }) {
  return <div className="equation" dangerouslySetInnerHTML={{ __html: katex.renderToString(tex, { displayMode: true, throwOnError: true }) }} />;
}
function M({ tex }: { tex: string }) {
  return <span dangerouslySetInnerHTML={{ __html: katex.renderToString(tex, { throwOnError: true }) }} />;
}

export default function Theory() {
  return (
    <>
      <h1>Theory</h1>
      <p className="lead">
        The equations and methods behind every calculation, in SI units with R = 8.31446261815324 J mol⁻¹ K⁻¹ (exact,
        2019 SI). Both phases are described by the same cubic equation of state (the φ–φ approach).
      </p>

      <h2>Cubic equations of state</h2>
      <p>All four equations are one generic cubic (Smith, Van Ness &amp; Abbott, 2005):</p>
      <Eq tex={String.raw`P = \frac{RT}{V-b} - \frac{a(T)}{(V+\varepsilon b)(V+\sigma b)},\qquad a_i = \Psi\,\alpha(T_{r,i},\omega_i)\,\frac{R^2T_{c,i}^2}{P_{c,i}},\qquad b_i = \Omega\,\frac{RT_{c,i}}{P_{c,i}}`} />
      <div className="table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Equation</th>
              <th>σ</th>
              <th>ε</th>
              <th>Ω</th>
              <th>Ψ</th>
              <th style={{ textAlign: "left" }}>α(T<sub>r</sub>, ω)</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>van der Waals (1873)</td>
              <td>0</td>
              <td>0</td>
              <td>1/8</td>
              <td>27/64</td>
              <td style={{ textAlign: "left" }}>1</td>
            </tr>
            <tr>
              <td>Redlich–Kwong (1949)</td>
              <td>1</td>
              <td>0</td>
              <td>0.0866403</td>
              <td>0.4274802</td>
              <td style={{ textAlign: "left" }}>
                <M tex={String.raw`T_r^{-1/2}`} />
              </td>
            </tr>
            <tr>
              <td>Soave–Redlich–Kwong (1972)</td>
              <td>1</td>
              <td>0</td>
              <td>0.0866403</td>
              <td>0.4274802</td>
              <td style={{ textAlign: "left" }}>
                <M tex={String.raw`\left[1+m\left(1-\sqrt{T_r}\right)\right]^2,\ m = 0.480+1.574\omega-0.176\omega^2`} />
              </td>
            </tr>
            <tr>
              <td>Peng–Robinson (1976)</td>
              <td>1+√2</td>
              <td>1−√2</td>
              <td>0.0777961</td>
              <td>0.4572355</td>
              <td style={{ textAlign: "left" }}>
                <M tex={String.raw`\left[1+\kappa\left(1-\sqrt{T_r}\right)\right]^2,\ \kappa = 0.37464+1.54226\omega-0.26992\omega^2`} />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <p>
        Ω and Ψ are the exact values that follow from the critical conditions{" "}
        <M tex={String.raw`(\partial P/\partial V)_T = (\partial^2 P/\partial V^2)_T = 0`} /> at (T<sub>c</sub>, P<sub>c</sub>), so every
        equation reproduces its components' critical point exactly (the papers print them rounded, e.g. 0.07780 and
        0.45724 for PR).
      </p>

      <h2>Mixtures</h2>
      <p>van der Waals one-fluid mixing, with optional binary interaction parameters k<sub>ij</sub>:</p>
      <Eq tex={String.raw`a = \sum_i\sum_j x_i x_j a_{ij},\quad a_{ij} = (1-k_{ij})\sqrt{a_i a_j},\qquad b = \sum_i x_i b_i,\qquad A = \frac{aP}{(RT)^2},\quad B = \frac{bP}{RT}`} />
      <p>The equation of state as a cubic in the compressibility factor Z = PV/RT:</p>
      <Eq tex={String.raw`Z^3 + \left[(\sigma+\varepsilon-1)B - 1\right]Z^2 + \left[A + \sigma\varepsilon B^2 - (\sigma+\varepsilon)B(B+1)\right]Z - \left[AB + \sigma\varepsilon B^2(B+1)\right] = 0`} />
      <p>
        Only roots with Z &gt; B are physical. The liquid takes the smallest, the vapour the largest; for a phase of
        unknown type, the root with the lowest Gibbs energy. Small liquid roots at low pressure are kept accurate by
        deflating the cubic after its largest root.
      </p>

      <h2>Fugacity coefficients</h2>
      <Eq tex={String.raw`\ln\hat\varphi_i = \frac{b_i}{b}(Z-1) - \ln(Z-B) - \frac{A}{B}\left(\frac{2\sum_j x_j a_{ij}}{a} - \frac{b_i}{b}\right) I,\qquad I = \frac{1}{\sigma-\varepsilon}\ln\frac{Z+\sigma B}{Z+\varepsilon B}`} />
      <p>
        with <M tex={String.raw`I = B/(Z+\varepsilon B)`} /> for van der Waals (σ = ε). Phases are in equilibrium when
        every component has the same fugacity in both: <M tex={String.raw`x_i\hat\varphi_i^L = y_i\hat\varphi_i^V`} />,
        i.e. <M tex={String.raw`K_i = y_i/x_i = \hat\varphi_i^L/\hat\varphi_i^V`} />.
      </p>

      <h2>Vapour pressure of a pure component</h2>
      <p>
        P<sup>sat</sup>(T) is where the liquid and vapour roots have equal fugacity. Between the two spinodal pressures
        (where ∂P/∂V = 0) the cubic has three roots and
      </p>
      <Eq tex={String.raw`f(P) = \ln\varphi^L - \ln\varphi^V,\qquad \frac{\partial f}{\partial \ln P} = Z^L - Z^V < 0`} />
      <p>
        so f has exactly one root there. PEC brackets P<sup>sat</sup> between the spinodals and solves with Brent's
        method: no initial guess, guaranteed convergence for every T below T<sub>c</sub>.
      </p>

      <h2>Stability and the flash</h2>
      <p>
        A feed z is stable if no trial phase w lowers its Gibbs energy: the tangent-plane test of Michelsen (1982). With{" "}
        <M tex={String.raw`d_i = \ln z_i + \ln\hat\varphi_i(z)`} />, two trial phases (vapour- and liquid-like, started
        from Wilson's K-values) are relaxed by
      </p>
      <Eq tex={String.raw`\ln W_i \leftarrow d_i - \ln\hat\varphi_i(w),\qquad w = W/\textstyle\sum W,\qquad \text{unstable if } \sum_i W_i > 1`} />
      <p>If the feed is unstable, the phase split follows from the Rachford–Rice equation (1952) for the vapour fraction V,</p>
      <Eq tex={String.raw`\sum_i \frac{z_i(K_i-1)}{1+V(K_i-1)} = 0,\qquad x_i = \frac{z_i}{1+V(K_i-1)},\quad y_i = K_i x_i`} />
      <p>
        solved by Brent's method between its poles, where the root is unique; K is updated from the fugacity
        coefficients until they agree to 10⁻¹⁰. Wilson's estimate starts the iterations:
      </p>
      <Eq tex={String.raw`\ln K_i = \ln\frac{P_{c,i}}{P} + 5.373\,(1+\omega_i)\left(1-\frac{T_{c,i}}{T}\right)`} />

      <h2>Bubble and dew points</h2>
      <p>
        At a bubble point the liquid z is in equilibrium with an incipient vapour y = Kz, and{" "}
        <M tex={String.raw`\sum_i K_i z_i = 1`} />; at a dew point the vapour z is in equilibrium with x = z/K, and{" "}
        <M tex={String.raw`\sum_i z_i/K_i = 1`} />. K is updated from the fugacity coefficients, and P or T by a Newton
        step on the logarithm of that sum. A result where K collapses to 1 (both phases the same) is never accepted.
      </p>

      <h2>Limits</h2>
      <ul>
        <li>Cubic equations with a generalised α are least accurate for polar and associating fluids (water, alcohols) and quantum gases (He, H₂).</li>
        <li>Two phases only (vapour–liquid). Liquid–liquid and three-phase equilibria are not covered yet.</li>
        <li>The phase envelope stops short of the mixture critical point; tracing through it comes in a later version.</li>
      </ul>

      <h2>References</h2>
      <ul>
        <li>van der Waals, J. D. (1873). Over de continuiteit van den gas- en vloeistoftoestand. Thesis, Leiden.</li>
        <li>Redlich, O., Kwong, J. N. S. (1949). Chem. Rev. 44, 233–244.</li>
        <li>Soave, G. (1972). Chem. Eng. Sci. 27, 1197–1203.</li>
        <li>Peng, D.-Y., Robinson, D. B. (1976). Ind. Eng. Chem. Fundam. 15, 59–64.</li>
        <li>Rachford, H. H., Rice, J. D. (1952). J. Pet. Technol. 4(10), 19.</li>
        <li>Wilson, G. M. (1969). AIChE 65th National Meeting, Cleveland, paper 15C.</li>
        <li>Michelsen, M. L. (1982). Fluid Phase Equilib. 9, 1–19 and 21–40.</li>
        <li>Michelsen, M. L., Mollerup, J. M. (2007). Thermodynamic Models: Fundamentals and Computational Aspects, 2nd ed. Tie-Line.</li>
        <li>Smith, J. M., Van Ness, H. C., Abbott, M. M. (2005). Introduction to Chemical Engineering Thermodynamics, 7th ed. McGraw-Hill.</li>
        <li>Bell, I. H., Wronski, J., Quoilin, S., Lemort, V. (2014). Ind. Eng. Chem. Res. 53, 2498–2508 (CoolProp, the source of the component data).</li>
      </ul>
    </>
  );
}
