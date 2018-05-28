package simpledb.server;

import simpledb.buffer.BufferMgr;
import simpledb.buffer.Buffer;
import simpledb.buffer.BufferAbortException;
import simpledb.file.Block;
import simpledb.remote.*;
import simpledb.tx.recovery.RecoveryMgr;
import java.rmi.registry.*;

public class Startup {
	public static void testRecovery1() {
		System.out.println("==================");
		Block blk1 = new Block("newFile", 2);
		int txid = 100;
		RecoveryMgr rm = new RecoveryMgr(499);
		rm.commit();
		rm.recover();
		System.out.println("==================");
		BufferMgr bm = SimpleDB.bufferMgr();
		bm.pin(blk1);
		Buffer buff = bm.getMapping(blk1);
		int offset = 4;
		int newVal = 1234;
		int lsn2 = rm.setString(buff, offset, "newVal499");
		buff.setString(offset, "newVal499", txid, lsn2);
		bm.flushAll(txid);
		rm.recover();
		System.out.println("==================");
	}

	/*
	 * For eg. Consider two transaction txid=1 and txid=2 Add following log
	 * record for txid=1 1. setInt( oldval=5, newval=10) [UPDATE log record] 2.
	 * Commit transaction for txid=1. [COMMIT log record] Add following log
	 * record for txid=2 3. setInt( oldval=5, newval=10) [UPDATE log record] 4.
	 * setString(oldval=â€œHelloâ€�,newval= â€�Worldâ€�) [UPDATE log record]
	 */
	public static void testRecovery2() {
		System.out.println("============================================================");
		Block blk1 = new Block("newFile", 2);
		BufferMgr bm = SimpleDB.bufferMgr();
		bm.pin(blk1);
		Buffer buff = bm.getMapping(blk1);
		int offset = 4;
		int txid11 = 1111;
		int txid22 = 2222;
		RecoveryMgr rm11 = new RecoveryMgr(txid11);
		RecoveryMgr rm22 = new RecoveryMgr(txid22);
		rm11.setInt(buff, offset, 5, 10);
		rm11.commit();

		rm22.setInt(buff, offset, 5, 10);
		rm22.setString(buff, offset, "Hello", "World");

		rm11.recover();
		System.out.println("============================================================");
		rm22.recover();

	}

	public static void testBufferPool() {

		Block blk1 = new Block("filename", 1);
		BufferMgr basicBufferMgr = new SimpleDB().bufferMgr();
		// basicBufferMgr.pin(blk1);

		try {
			basicBufferMgr.pin(blk1);

			// Creating buffers
			Block[] blks = new Block[11];
			System.out.println("Initially: " + basicBufferMgr.available());
			for (int i = 1; i <= 10; i++) {
				blks[i] = new Block("filename" + i, i);
			}
			// pinning buffers
			for (int i = 1; i <= 7; i++) {
				basicBufferMgr.pin(blks[i]);
				System.out.println("Available buffers: " + basicBufferMgr.available());
			}
			System.out.println("End:" + basicBufferMgr.available());
			// unpinning buffers
			basicBufferMgr.unpin(basicBufferMgr.getMapping(blks[3]));
			basicBufferMgr.unpin(basicBufferMgr.getMapping(blks[2]));
			System.out.println("after unpin 2blks:" + basicBufferMgr.available());
			// checking if the already pinned buffer is picked from the buffer
			// pool
			System.out.println("Blk[1] present " + basicBufferMgr.containsMapping(blks[1]));
			basicBufferMgr.pin(blks[1]);
			System.out.println("Blk[9] present " + basicBufferMgr.containsMapping(blks[9]));

			basicBufferMgr.pin(blks[9]);

			basicBufferMgr.pin(blks[10]);
			basicBufferMgr.pin(blks[8]);

		} catch (BufferAbortException e) {
			System.out.println("got BufferAbortException exception ");
			System.out.println(e.getMessage());
		}

		// pin(1), pin(2), pin(3), pin(4), pin(5), pin(6), pin(7), pin(8),
		// unpin(3), unpin(2).

	}

	public static void main(String args[]) throws Exception {
		// configure and initialize the database
		// SimpleDB.init(args[0]);
		SimpleDB.init("simpledb");

		// create a registry specific for the server on the default port
		Registry reg = LocateRegistry.createRegistry(1099);

		// and post the server entry in it
		RemoteDriver d = new RemoteDriverImpl();
		reg.rebind("simpledb", d);

		System.out.println("database server ready");

		// Uncomment to test accordingly
		// testBufferPool();
		// testRecovery1();
		// testRecovery2();
	}

}
