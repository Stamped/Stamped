//
//  CreateImageViewController.m
//  FontTest
//
//  Created by Kevin Palms on 7/8/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import "CreateImageViewController.h"


@implementation CreateImageViewController


- (id)initWithNibName:(NSString *)nibNameOrNil bundle:(NSBundle *)nibBundleOrNil
{
    self = [super initWithNibName:nibNameOrNil bundle:nibBundleOrNil];
    if (self) {
        // Custom initialization
      NSLog(@"Begin");
    }
    return self;
}

- (void)dealloc
{
    [super dealloc];
}

- (void)didReceiveMemoryWarning
{
    // Releases the view if it doesn't have a superview.
    [super didReceiveMemoryWarning];
    
    // Release any cached data, images, etc that aren't in use.
}

#pragma mark - View lifecycle

-(UIImage *)imageFromText:(NSString *)text
{
  // set the font type and size
  UIFont *font = [UIFont fontWithName:@"TGLight" size:42];  
  CGSize size  = [text sizeWithFont:font];
  
  NSLog(@"Size: %@", NSStringFromCGSize(size));
  
  // check if UIGraphicsBeginImageContextWithOptions is available (iOS is 4.0+)
  if (UIGraphicsBeginImageContextWithOptions != NULL)
    UIGraphicsBeginImageContextWithOptions(size,NO,0.0);
  else
    // iOS is < 4.0 
    UIGraphicsBeginImageContext(size);
  
  // draw in context, you can use also drawInRect:withFont:
  [text drawAtPoint:CGPointMake(0.0, 0.0) withFont:font];
  
  // transfer image
  UIImage *image = UIGraphicsGetImageFromCurrentImageContext();
  UIGraphicsEndImageContext();    
  
  return image;
}

- (void)mailComposeController:(MFMailComposeViewController*)controller didFinishWithResult:(MFMailComposeResult)result error:(NSError*)error {
//	[self becomeFirstResponder];
//	[self dismissModalViewControllerAnimated:YES];

  [self dismissModalViewControllerAnimated:YES];
}

-(void)displayComposerSheet
{
  NSLog(@"Begin");
	MFMailComposeViewController *picker = [[MFMailComposeViewController alloc] init];
	picker.mailComposeDelegate = self;
	
	[picker setSubject:@"Hello from California!"];
  
  UIImage *textImage = [self imageFromText:@"Little Owl"];
	
	// Attach an image to the email
//	NSString *path = [[NSBundle mainBundle] pathForResource:@"rainy" ofType:@"png"];
  NSData *textImageData = UIImagePNGRepresentation(textImage);
	[picker addAttachmentData:textImageData mimeType:@"image/png" fileName:@"rainy"];
	
	// Fill out the email body text
	NSString *emailBody = @"<h1>Stamped!</h1><p>Check it out</p><p><img src='rainy.png'></p><p>No, really...</p>";
	[picker setMessageBody:emailBody isHTML:YES];
	
	[self presentModalViewController:picker animated:YES];
  [picker release];
}


/*
// Implement loadView to create a view hierarchy programmatically, without using a nib.
- (void)loadView
{
}
*/


// Implement viewDidLoad to do additional setup after loading the view, typically from a nib.
- (void)viewDidLoad
{
  
  UIImage *image = [self imageFromText:@"This is a text"];
  [self.view addSubview:[[UIImageView alloc] initWithImage:image]];
  
  UIButton *newButton = [[UIButton alloc] init];
  newButton.frame = CGRectMake(10, 50, 40, 40);
  [newButton setBackgroundColor:[UIColor blueColor]];
  [newButton setTitle:@"Test" forState:UIControlStateNormal];
  [newButton addTarget:self action:@selector(displayComposerSheet) forControlEvents:UIControlEventTouchUpInside];
//  button.center = self.view.center;
  [self.view addSubview:newButton];
  [newButton release];
}

- (void)viewDidAppear:(BOOL)animated
{
  
}

- (void)viewDidUnload
{
    [super viewDidUnload];
    // Release any retained subviews of the main view.
    // e.g. self.myOutlet = nil;
}

@end
