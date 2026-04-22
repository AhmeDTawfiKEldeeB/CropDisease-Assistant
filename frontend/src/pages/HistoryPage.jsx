import { Link } from "react-router-dom";
import Layout from "../components/Layout";
import PageTransition from "../components/PageTransition";
import Card from "../components/Card";
import { historyItems } from "../data/mockData";
import { useI18n } from "../hooks/useI18n";

const severityClass = {
  low: "bg-emerald-100 text-emerald-800",
  medium: "bg-amber-100 text-amber-800",
  high: "bg-rose-100 text-rose-800",
};

export default function HistoryPage() {
  const { t } = useI18n();

  return (
    <PageTransition>
      <Layout title={t.history.title} subtitle={t.history.subtitle}>
        <Card>
          <h3 className="mb-5 text-xl font-black">{t.history.recent}</h3>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[740px] text-left text-sm">
              <thead className="text-on-surface-variant">
                <tr>
                  <th className="pb-3 font-semibold">ID</th>
                  <th className="pb-3 font-semibold">Plant</th>
                  <th className="pb-3 font-semibold">Disease</th>
                  <th className="pb-3 font-semibold">Confidence</th>
                  <th className="pb-3 font-semibold">Date</th>
                  <th className="pb-3 font-semibold">Severity</th>
                  <th className="pb-3 font-semibold">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-variant/40">
                {historyItems.map((item) => (
                  <tr key={item.id} className="transition hover:bg-surface-container-low dark:hover:bg-slate-800">
                    <td className="py-4 font-semibold">{item.id}</td>
                    <td className="py-4">{item.plant}</td>
                    <td className="py-4">{item.disease}</td>
                    <td className="py-4 font-semibold text-primary">{item.confidence}%</td>
                    <td className="py-4">{item.date}</td>
                    <td className="py-4">
                      <span className={`rounded-full px-3 py-1 text-xs font-bold ${severityClass[item.severity]}`}>{item.severity}</span>
                    </td>
                    <td className="py-4">
                      <Link to="/diagnosis" className="rounded-full bg-primary px-4 py-2 text-xs font-bold text-white transition hover:scale-95">
                        {t.history.details}
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      </Layout>
    </PageTransition>
  );
}