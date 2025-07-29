export default function Home() {
  return (
    <div className="col-center gap-4  pt-4">
      <div className="w-full center gap-4 h-[45vh]">
        <section className="w-[80%] h-[45vh] bg-surface-3-dark rounded-default p-4 border border-border-dark">
          <p>Graph 1</p>
        </section>

        <section className="w-[20%] h-[45vh] bg-surface-3-dark rounded-default p-4 border border-border-dark">
          <p>Info 1</p>
        </section>
      </div>
      <div className="w-full center gap-4 h-[45vh]">
        <section className="w-1/2 h-[45vh] bg-surface-3-dark rounded-default p-4 border border-border-dark">
          <p>Logs</p>
        </section>

        <section className="w-1/2 h-[45vh] bg-surface-3-dark rounded-default p-4 border border-border-dark">
          <p>Graph 2</p>
        </section>
      </div>
    </div>
  );
}
