/*
 * Refactor base on MACROS
 */ 

#include <openssl/conf.h>
#include <openssl/evp.h>
#include <openssl/err.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>
#include <stdint.h>

#define ENCRYPT_METHOD EVP_aes_256_gcm

// Key size for benchmark: 16, 24 or 32
#define KEY_SIZE (32)

// 
uint64_t rdtsc(){
    unsigned int lo,hi;
    __asm__ __volatile__ ("rdtsc" : "=a" (lo), "=d" (hi));
    return ((uint64_t)hi << 32) | lo;
}

void handleErrors(void)
{
  ERR_print_errors_fp(stderr);
  abort();
}


void fill_with_random(unsigned char *stream, int n)
{
  size_t i;
  for (i = 0; i < n; i++)
  {
    stream[i] = (unsigned char) (rand() % 255 + 1);
  }
  stream[n] = 0;
}


// note that we can't have a 0 value byte only at stream end
unsigned char* gen_random_bytestream(int num_bytes)
{
  /* make sure we don't include a 0 */
  unsigned char* stream=malloc(num_bytes + 1);
  if (stream == NULL)
    {
        printf("ERROR : Could not allocate memory for random buffer !");
    }

    fill_with_random(stream, num_bytes);
  return stream;
}


int decrypt(unsigned char *ciphertext, int ciphertext_len, unsigned char *aad,
	int aad_len, unsigned char *tag, unsigned char *key, unsigned char *iv,
	unsigned char *plaintext)
{
	EVP_CIPHER_CTX *ctx;
	int len;
	int plaintext_len;
	int ret;

	/* Create and initialise the context */
	if(!(ctx = EVP_CIPHER_CTX_new())) handleErrors();

	/* Initialise the decryption operation. */
	if(!EVP_DecryptInit_ex(ctx, ENCRYPT_METHOD(), NULL, NULL, NULL))
		handleErrors();

	/* Set IV length. Not necessary if this is 12 bytes (96 bits) */
	//if(!EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, 16, NULL))
	//	handleErrors();

	/* Initialise key and IV */
	if(!EVP_DecryptInit_ex(ctx, NULL, NULL, key, iv)) handleErrors();

	/* Provide any AAD data. This can be called zero or more times as
	 * required
	 */
	if(!EVP_DecryptUpdate(ctx, NULL, &len, aad, aad_len))
		handleErrors();

	/* Provide the message to be decrypted, and obtain the plaintext output.
	 * EVP_DecryptUpdate can be called multiple times if necessary
	 */
	if(!EVP_DecryptUpdate(ctx, plaintext, &len, ciphertext, ciphertext_len))
		handleErrors();
	plaintext_len = len;

	/* Set expected tag value. Works in OpenSSL 1.0.1d and later */
	if(!EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_TAG, 16, tag))
		handleErrors();

	/* Finalise the decryption. A positive return value indicates success,
	 * anything else is a failure - the plaintext is not trustworthy.
	 */
	ret = EVP_DecryptFinal_ex(ctx, plaintext + len, &len);

	/* Clean up */
	EVP_CIPHER_CTX_free(ctx);

	if(ret > 0)
	{
		/* Success */
		plaintext_len += len;
		return plaintext_len;
	}
	else
	{
		/* Verify failed */
		return -1;
	}
}

int encrypt(unsigned char *plaintext, int plaintext_len, unsigned char *aad,
	int aad_len, unsigned char *key, unsigned char *iv,
	unsigned char *ciphertext, unsigned char *tag)
{
	EVP_CIPHER_CTX *ctx;

	int len;

	int ciphertext_len;


	/* Create and initialise the context */
	if(!(ctx = EVP_CIPHER_CTX_new())) handleErrors();

	/* Initialise the encryption operation. */
	if(1 != EVP_EncryptInit_ex(ctx, ENCRYPT_METHOD(), NULL, NULL, NULL))
		handleErrors();

	/* Set IV length if default 12 bytes (96 bits) is not appropriate */
	//if(1 != EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, 16, NULL))
	//	handleErrors();

	/* Initialise key and IV */
	if(1 != EVP_EncryptInit_ex(ctx, NULL, NULL, key, iv)) handleErrors();

	/* Provide any AAD data. This can be called zero or more times as
	 * required
	 */
	//if(1 != EVP_EncryptUpdate(ctx, NULL, &len, aad, aad_len))
	//	handleErrors();

	/* Provide the message to be encrypted, and obtain the encrypted output.
	 * EVP_EncryptUpdate can be called multiple times if necessary
	 */
	if(1 != EVP_EncryptUpdate(ctx, ciphertext, &len, plaintext, plaintext_len))
		handleErrors();
	ciphertext_len = len;

	/* Finalise the encryption. Normally ciphertext bytes may be written at
	 * this stage, but this does not occur in GCM mode
	 */
	if(1 != EVP_EncryptFinal_ex(ctx, ciphertext + len, &len)) handleErrors();
	ciphertext_len += len;

	/* Get the tag */
	if(1 != EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_GET_TAG, 16, tag))
		handleErrors();

	/* Clean up */
	EVP_CIPHER_CTX_free(ctx);

	return ciphertext_len;
}


int main (void)
{
    // library initialization, not included in timing
    ERR_load_crypto_strings();
    OpenSSL_add_all_algorithms();
    // config is deprecated as of v1.1
    //OPENSSL_config(NULL);

    // test parameters
    int         repetitions = 10;

    int         iv_size = 16; // should be identical to AES block size, i.e. 128 bits

    clock_t     start_time, end_time;
    double      cpu_time_used;
    double      total_time = 0;  
    
    uint64_t    start_cycles, end_cycles, total_cycles;
    uint64_t    start_cycles_decrypt, end_cycles_decrypt, total_cycles_decrypt;
    uint64_t    cycles_avg = 0;
    int data_size_kb;
   // for(data_size_kb=64 * 1024; data_size_kb>=1024; data_size_kb-=1024)
    

    for(data_size_kb=512; data_size_kb<=64 * 1024; data_size_kb+=512)
    {
        int data_size = 1024 * data_size_kb;
                
        unsigned char *rand_plaintxt = gen_random_bytestream(data_size);
        unsigned char *ciphertext = (unsigned char *)malloc(data_size + 1); 
            ciphertext[data_size] = 0;
        unsigned char *decryptedtext = (unsigned char *)malloc(data_size + 1);
        int plaintext_len = strlen ((char *)rand_plaintxt);
        unsigned char *tag=(unsigned char *)malloc(32);


        total_time = 0;
        total_cycles = 0;    
        total_cycles_decrypt = 0;

        for(int r=0; r<repetitions; r++)
        {
            unsigned char *_k = gen_random_bytestream(KEY_SIZE);
            unsigned char *_iv = gen_random_bytestream(16);

            // within experiments it doesnt make any difference randomizing 
            // each time, therefore commenting the randomization for speed
            // fill_with_random(rand_plaintxt, data_size);

            // do an encrypt for mearusing TIME ticks
            start_time = clock();
            //encrypt(rand_plaintxt, plaintext_len, _k, _iv, ciphertext);
            end_time = clock();        
            double time_taken = (double)(end_time - start_time)/CLOCKS_PER_SEC;
            total_time += time_taken;

            // do an ecrypt for measuring CYCLES
            start_cycles = rdtsc();
            int len = encrypt(rand_plaintxt, plaintext_len, (unsigned char *)"", 0, 
                _k, _iv, ciphertext, tag);
            end_cycles = rdtsc();
            total_cycles += (end_cycles - start_cycles); 
    
            
            // measure decrypt CYCLES
            start_cycles_decrypt = rdtsc();                  
            int r = decrypt(ciphertext, len, (unsigned char *)"", 0,
                tag, _k, _iv, decryptedtext);
            if (r == -1) printf("AUTHENTICATION FAILED !!!");
            end_cycles_decrypt = rdtsc();
            total_cycles_decrypt += (end_cycles_decrypt - start_cycles_decrypt);
                    
        }


        double avg_time = total_time/repetitions;
        double avg_cycles = (double)total_cycles/repetitions;
        double avg_cpb = ((double)total_cycles/repetitions)/data_size;
        double mb_s = (((double)(data_size * repetitions))/total_time) / (1024 * 1024); 
        double avg_cycles_decrypt = (double)total_cycles_decrypt/repetitions;
        
        printf("%8f\n", avg_cycles_decrypt);
    }
/*  

    total_time ..... data_size * reps
    1s         ..... x

  start = clock();
  s = rdtsc();
  ciphertext_len = encrypt (plaintext, strlen ((char *)plaintext), key, iv,
                            ciphertext);

  e = rdtsc();
  cycles = e - s;
  printf("Processor cycles : %" PRIu64 "\n", cycles);
  //printf("encrypt took %hu cycles \n", cycles);
    

  end = clock();
  double t = end - start;  
  double time_taken = (double)t/CLOCKS_PER_SEC; // in seconds
  printf("encrypt took %f seconds to execute \n", time_taken);


  printf("Ciphertext is:\n");
  BIO_dump_fp (stdout, (const char *)ciphertext, ciphertext_len);

  decryptedtext_len = decrypt(ciphertext, ciphertext_len, key, iv,
    decryptedtext);

  decryptedtext[decryptedtext_len] = '\0';

  printf("Decrypted text is:\n");
  printf("%s\n", decryptedtext);
*/

  // library shutdown - should not be timed
  EVP_cleanup();
  ERR_free_strings();

  return 0;
}
