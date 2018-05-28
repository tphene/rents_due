package simpledb.buffer;

import simpledb.buffer.Buffer;
import simpledb.buffer.BufferMgr;
import simpledb.file.Block;
import simpledb.server.SimpleDB;

public class TestBufferManager {

	public static void main(String[] args) {
		// TODO Auto-generated method stub
		SimpleDB.init("simpleDB");
		BufferMgr bm = new BufferMgr(3);

		Block [] blockArray = new Block [10];
		//Block blk1 = new Block("blk1.txt", 1);
		for(int i=0;i<10;i++) {
			blockArray[i] = new Block("blk"+i+".txt", i);			
		}

		bm.pin(blockArray[1]);
		bm.pin(blockArray[2]);
		bm.pin(blockArray[3]);

		Buffer buff = null;

		buff = bm.findExistingBuffer(blockArray[1]);
		if(buff!=null)
			bm.unpin(buff);

		buff = bm.findExistingBuffer(blockArray[2]);
		if(buff!=null)
			bm.unpin(buff);
		
		bm.pin(blockArray[1]);
		
		buff = bm.findExistingBuffer(blockArray[1]);
		if(buff!=null)
			bm.unpin(buff);

		bm.pin(blockArray[4]);

		printBufferPool(bm.getBufferPool());
	}

	private static void printBufferPool(Buffer [] bufferPool) {
		System.out.println("************************************");
		for(int i=0;i<bufferPool.length;i++) {
			Buffer buffer = bufferPool[i];
			if(buffer !=null) {
				Block blk = buffer.block();
				if(blk!=null) {
					System.out.println(i+" - "+ blk.fileName()+" - Pin count = "+buffer.getPins());
				}
			}
		}
	}

}
