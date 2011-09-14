//
//  WrappingText.m
//  Stamped
//
//  Created by Jake Zien on 9/13/11.
//  Copyright 2011 RISD. All rights reserved.
//

#import "WrappingText.h"
#import "CollapsibleViewController.h"

@implementation WrappingText

@synthesize topTextView = topTextView_;
@synthesize bottomTextView = bottomTextView_;
@synthesize text  = text_;
@synthesize container = container_;

- (id)initWithNibName:(NSString *)nibNameOrNil bundle:(NSBundle *)nibBundleOrNil
{
    self = [super initWithNibName:nibNameOrNil bundle:nibBundleOrNil];
    if (self) {
        // Custom initialization
    }
    return self;
}

- (void)didReceiveMemoryWarning
{
    // Releases the view if it doesn't have a superview.
    [super didReceiveMemoryWarning];
    
    // Release any cached data, images, etc that aren't in use.
}

#pragma mark - View lifecycle

- (void)viewDidLoad
{
    [super viewDidLoad];
    // Do any additional setup after loading the view from its nib.
}

- (void)viewDidUnload
{
    [super viewDidUnload];
    // Release any retained subviews of the main view.
    // e.g. self.myOutlet = nil;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation
{
    // Return YES for supported orientations
    return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

#pragma mark - Managing the UITextViews
-(void)setText:(NSString *)newText
{
  text_ = newText;
  
  topTextView_.text = self.text;
  
  NSLog(@"%@", text_);
  
  NSString* topText = text_;
  NSString* bottomText = text_;
  
  CGSize size = [topTextView_.text sizeWithFont:topTextView_.font
                              constrainedToSize:CGSizeMake(topTextView_.frame.size.width, HUGE_VAL)
                                  lineBreakMode:UILineBreakModeWordWrap];
  

  /*
  while (size.height > (self.container.collapsedHeight - self.container.headerView.frame.size.height -
                        self.container.footerView.frame.size.height))
  {
    topText = [topText substringToIndex:topText.length - 1];
    topTextView_.text = topText;
    size = [topTextView_.text sizeWithFont:topTextView_.font
                         constrainedToSize:CGSizeMake(topTextView_.frame.size.width, HUGE_VAL)
                             lineBreakMode:UILineBreakModeWordWrap];
  }
  
  topTextView_.text = topText;
  CGRect frame = topTextView_.frame;
  frame.size = size;
  topTextView_.frame = frame;
   */
}

@end
