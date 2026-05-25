def main() -> None:
    """Start the Phase 1 worker placeholder.

    What: Boots a no-op process that proves compose can start a worker
        container.
    Why: Later processing phases need a reserved worker service name, but
        Phase 1 must not enqueue or process reconciliation jobs.

    States / Side Effects:
        Writes a startup log line and then exits successfully.
    """
    print("ReconAI Phase 1 worker placeholder started; no jobs processed.")


if __name__ == "__main__":
    main()
