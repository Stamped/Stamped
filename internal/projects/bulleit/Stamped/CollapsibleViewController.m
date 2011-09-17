  //
//  CollapsibleViewController.m
//  Stamped
//
//  Created by Jake Zien on 9/7/11.
//  Copyright 2011 RISD. All rights reserved.
//

#import <QuartzCore/QuartzCore.h>

#import "CollapsibleViewController.h"
#import "PairedLabel.h"
#import "WrappingTextView.h"
#import "UIColor+Stamped.h"
#import "Stamp.h"
#import "User.h"
#import "MediumUserImageButton.h"
#import "StampDetailViewController.h"
#import "StampedAppDelegate.h"

 
@implementation CollapsibleViewController

@synthesize headerView      = headerView_;
@synthesize contentView     = contentView_;
@synthesize sectionLabel    = sectionLabel_;
@synthesize arrowView       = arrowView_;
@synthesize isCollapsed     = isCollapsed_;
@synthesize contentDict     = contentDict_;
@synthesize numLabel        = numLabel_;
@synthesize iconView        = iconView_;
@synthesize delegate        = delegate_;
@synthesize collapsedHeight = collapsedHeight_;
@synthesize footerView      = footerView_;
@synthesize footerLabel     = footerLabel_;
@synthesize collapsedFooterText = collapsedFooterText_;
@synthesize expandedFooterText  = expandedFooterText_; 
@synthesize imageView       = imageView_;
@synthesize stamps          = stamps_;

int const LABEL_HEIGHT          = 20;
int const IMAGE_HEIGHT          = 40;
int const SPACE_HEIGHT          = 10;

- (id)initWithNibName:(NSString *)nibNameOrNil bundle:(NSBundle *)nibBundleOrNil
{
    self = [super initWithNibName:nibNameOrNil bundle:nibBundleOrNil];
    if (self) {
      isCollapsed_ = YES;
      collapsedHeight_ = 40.f;
      
      if ([nibNameOrNil isEqualToString:@"CollapsiblePreviewController"]) previewMode = YES;

      NSMutableDictionary* dict = [NSMutableDictionary dictionary];
      contentDict_ = dict;
      [contentDict_ retain];
      
      maxNameLabelWidth = 0.f;
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
  self.arrowView.image = [UIImage imageNamed:@"eDetail-arrow-down"];
}

- (void)viewDidUnload
{
    [super viewDidUnload];
    // Release any retained subviews of the main view.
    // e.g. self.myOutlet = nil;
  [contentDict_ removeAllObjects];
  [contentDict_ release];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation
{
    // Return YES for supported orientations
    return (interfaceOrientation == UIInterfaceOrientationPortrait);
}


#pragma mark - Collapsing and expanding

- (void)collapse
{
  [self.delegate collapsibleViewController:self willChangeHeightBy:collapsedHeight_-self.view.bounds.size.height];
  self.view.frame = CGRectMake(self.view.frame.origin.x, self.view.frame.origin.y,
                               self.view.frame.size.width, collapsedHeight_);
  
  if (self.footerLabel)
  {
    self.footerLabel.text = self.collapsedFooterText;
    CGFloat delta = CGRectGetMinX(self.footerLabel.frame) + [self.footerLabel.text sizeWithFont:self.footerLabel.font].width - CGRectGetMinX(arrowView_.frame);
    arrowView_.frame = CGRectOffset(arrowView_.frame, delta, 0);
  }
}

- (void)expand
{
  CGFloat newHeight = 40.f + [self contentHeight] + SPACE_HEIGHT;
  if (self.footerView) newHeight += self.footerView.frame.size.height - SPACE_HEIGHT;
  
  [self.delegate collapsibleViewController:self willChangeHeightBy:newHeight - self.view.bounds.size.height];
  
  self.view.frame = CGRectMake(self.view.frame.origin.x, self.view.frame.origin.y,
                               self.view.frame.size.width, newHeight);
  
  if (self.footerLabel)
  {
    self.footerLabel.text = self.expandedFooterText;
    CGFloat delta = CGRectGetMinX(self.footerLabel.frame) + [self.footerLabel.text sizeWithFont:self.footerLabel.font].width - CGRectGetMinX(arrowView_.frame);
    arrowView_.frame = CGRectOffset(arrowView_.frame, delta, 0);
  }
  
}

- (void)swapArrowImage  //so the shadow always comes from the top edge.
{
  if (isCollapsed_)
  {
    arrowView_.transform = CGAffineTransformMakeRotation(0);
    arrowView_.image = [UIImage imageNamed:@"eDetail-arrow-down"]; 
  }
  
  else
  {
    arrowView_.transform = CGAffineTransformMakeRotation(0);
    arrowView_.image = [UIImage imageNamed:@"eDetail-arrow-up"]; 
  }
  
}

- (void)collapseAnimated
{
  
  [UIView animateWithDuration:0.25 
                   animations:^{ [self collapse];
                                 arrowView_.transform = CGAffineTransformMakeRotation(M_PI);}
                   completion:^(BOOL finished) { [self swapArrowImage]; } ];
}

- (void)expandAnimated
{  
  [UIView animateWithDuration:0.25
                   animations:^{ [self expand];
                                 arrowView_.transform = CGAffineTransformMakeRotation(M_PI); }
                   completion:^(BOOL finished) { [self swapArrowImage]; } ];
}


- (void)setIsCollapsed:(BOOL)collapsed
{
  isCollapsed_=collapsed;
  
  if (isCollapsed_) [self collapseAnimated];
  else [self expandAnimated];
}


#pragma mark - Adding content

- (void)addPairedLabelWithName:(NSString*)name value:(NSString*)value forKey:(NSString*)key {
  PairedLabel* newLabel = [[PairedLabel alloc] initWithNibName:@"PairedLabel" bundle:nil];

  CGRect frame = newLabel.view.frame;
  frame.origin = CGPointMake(sectionLabel_.frame.origin.x, [self contentHeight]);
  newLabel.view.frame = frame;
  
  newLabel.nameLabel.text  = name;
  newLabel.valueLabel.text = value;
  
  CGFloat newWidth = [newLabel.nameLabel.text sizeWithFont:newLabel.nameLabel.font].width;
  if (newWidth > maxNameLabelWidth)
  {
    maxNameLabelWidth = newWidth;
    
    for (UIViewController* vc in self.contentDict.objectEnumerator)
    {
      if ([vc isKindOfClass:[PairedLabel class]])
      {
        ((PairedLabel*)vc).nameWidth = maxNameLabelWidth;
      }                           
    }
  }
  
  newLabel.nameWidth = maxNameLabelWidth;
  
  [self addContent:newLabel forKey:key];
}

- (void)addNumberedListWithValues:(NSArray*)values {
  NSUInteger itemNumber = 0;
  
  for (NSString* value in values) {
    
    PairedLabel* newLabel = [[PairedLabel alloc] initWithNibName:@"PairedLabel" bundle:nil];
    
    CGRect frame = newLabel.view.frame;
    frame.origin = CGPointMake(sectionLabel_.frame.origin.x, [self contentHeight]);
    frame.size   = CGSizeMake(contentView_.frame.size.width, 16.f); 
    newLabel.view.frame = frame;
    
    //Change "label" field font for numbering.
    newLabel.nameLabel.font      = [UIFont fontWithName:@"Helvetica-Bold" size:10.f];
    newLabel.nameLabel.textColor = [UIColor stampedLightGrayColor];
    
    newLabel.nameLabel.text  = [NSString stringWithFormat:@"%d", ++itemNumber];
    newLabel.valueLabel.text = value;
    
    
    CGFloat newWidth = [newLabel.nameLabel.text sizeWithFont:newLabel.nameLabel.font].width;
    if (newWidth > maxNameLabelWidth)
    {
      maxNameLabelWidth = newWidth;
      
      for (UIViewController* vc in self.contentDict.objectEnumerator)
      {
        if ([vc isKindOfClass:[PairedLabel class]])
        {
          ((PairedLabel*)vc).numberWidth = maxNameLabelWidth;
        }                           
      }
    }
    
    newLabel.numberWidth = maxNameLabelWidth;
    
    [self addContent:newLabel forKey:[NSString stringWithFormat:@"%d", itemNumber]];
  
  }
  
}

- (void)addText:(NSString*)text forKey:(NSString*)key {
  UITextView* textView = [[UITextView alloc] initWithFrame:contentView_.frame];
  textView.font = [UIFont fontWithName:@"Helvetica" size:12.f];
  textView.textColor = [UIColor stampedGrayColor];
  textView.text = text;
  textView.backgroundColor = [UIColor clearColor];
  textView.userInteractionEnabled = NO;
  textView.frame = CGRectMake(8.f, 0.f, contentView_.frame.size.width-15.0, 100.0);
  
  [self addContent:textView forKey:key];
  CGRect frame = textView.frame;
  frame.size.height = textView.contentSize.height;
  textView.frame = frame;
}

- (void)addWrappingText:(NSString*)text forKey:(NSString*)key {
  
  CGRect frame = CGRectMake(15.f, 0.0, contentView_.frame.size.width-30.0, 10.0);
  CGSize previewRectSize = CGSizeMake(0,0);
  
  if (self.imageView)
    if (self.imageView.hidden == NO) {
      CGRect  imageViewFrame   = [self.contentView convertRect:self.imageView.frame fromView:self.imageView.superview];
      previewRectSize = CGSizeMake( CGRectGetMinX(self.imageView.frame) - 25.0,  CGRectGetMaxY(imageViewFrame) + 12.0 );
    }
  
  WrappingTextView* wrapText = [[WrappingTextView alloc] initWithFrame:frame text:text];
  wrapText.previewRectSize = previewRectSize;
//  NSLog(@"previewRectSize: %f %f", wrapText.previewRectSize.width, wrapText.previewRectSize.height);

  
  [self addContent:wrapText forKey:key];
}

- (void)addImagesForStamps:(NSSet*)newStamps
{
  NSSortDescriptor* desc = [NSSortDescriptor sortDescriptorWithKey:@"created" ascending:YES];
  NSArray* stampsArray = [newStamps sortedArrayUsingDescriptors:[NSArray arrayWithObject:desc]];
  stampsArray = [stampsArray filteredArrayUsingPredicate:[NSPredicate predicateWithFormat:@"temporary == NO"]];
  
  stamps_ = stampsArray;
  [stamps_ retain];
  
  UIScrollView* scrollView = [[UIScrollView alloc] initWithFrame:contentView_.frame];
  scrollView.frame = CGRectMake(0.f, 0.f, contentView_.frame.size.width, 58.0);
  scrollView.userInteractionEnabled = YES;
  scrollView.bounces = YES;
  scrollView.contentSize = CGSizeMake(scrollView.frame.size.width + 1.0, scrollView.frame.size.height);
  scrollView.showsHorizontalScrollIndicator = NO;
  scrollView.showsVerticalScrollIndicator = NO;
  scrollView.pagingEnabled = YES;
  
  CGRect userImgFrame = CGRectMake(0.0, 0.0, 43.0, 43.0);
  
  Stamp* s = nil;
  NSUInteger pageNum = 1;
  for (NSUInteger i = 0; i < stamps_.count; ++i) {
    s = [stamps_ objectAtIndex:i];
    MediumUserImageButton* userImageButton = [[MediumUserImageButton alloc] initWithFrame:userImgFrame];
    
    if (i > 1  &&  i % 6 == 0) {
      scrollView.contentSize = CGSizeMake(scrollView.contentSize.width + scrollView.frame.size.width, scrollView.contentSize.height);
      pageNum++;
    }
    
    CGFloat xOffset = i*(userImgFrame.size.width + 7.0) + 18.0 * (pageNum-1) + 14.0;
    
    userImageButton.frame = CGRectOffset(userImgFrame, xOffset, 0.0);
    userImageButton.contentMode = UIViewContentModeCenter;
    userImageButton.layer.shadowOffset = CGSizeMake(0.0, 1.0);
    userImageButton.layer.shadowOpacity = 0.20;
    userImageButton.layer.shadowRadius = 1.75;
    userImageButton.imageURL = s.user.profileImageURL;
    
    [userImageButton addTarget:self
                        action:@selector(userImageTapped:)
              forControlEvents:UIControlEventTouchUpInside];
    userImageButton.tag = i;
    [scrollView addSubview:userImageButton];
    [userImageButton release];
    
  }
  
  self.numLabel.text = [NSString stringWithFormat:@"(%d)", stamps_.count];
  self.numLabel.hidden = NO;
  
  [self addContent:scrollView forKey:@"stamps"];
}

- (void)addContent:(id)content forKey:(NSString*)key {
  [self.contentDict setObject:content forKey:key];
  if ([content respondsToSelector:@selector(view)])
      [contentView_ addSubview:((CollapsibleViewController*)content).view];
  else [contentView_ addSubview:(UIView*)content];
  
  if (self.footerLabel.hidden == NO  &&  self.contentHeight <= self.contentView.frame.size.height) {
    self.footerLabel.hidden = YES;
    self.arrowView.hidden = YES;
    self.collapsedHeight = self.headerView.frame.size.height + self.contentHeight;

//    CGRect footerFrame = self.footerView.frame;
//    footerFrame.size.height = 20;
//    footerFrame.origin.y -= 20;
//    self.footerView.frame = footerFrame;
    
    CGRect contentFrame = self.contentView.frame;
    contentFrame.size.height +=20;
    self.contentView.frame = contentFrame;
    
    CGRect viewFrame = self.view.frame;
    viewFrame.size.height = CGRectGetMaxY(self.footerView.frame) -20;
    self.view.frame = viewFrame;
    
        
  }
  
  if (self.footerLabel.hidden == YES && self.contentHeight > self.contentView.frame.size.height) {
    self.collapsedHeight = self.headerView.frame.size.height + self.contentHeight;
    self.footerLabel.hidden = NO;
    self.arrowView.hidden = NO;
    
    CGRect contentFrame = self.contentView.frame;
    contentFrame.size.height -= 20;
    self.contentView.frame = contentFrame;
    
    CGRect viewFrame = self.view.frame;
    viewFrame.size.height = CGRectGetMaxY(self.footerView.frame) +20;
    self.view.frame = viewFrame;
  }
  
  [content release];
}

- (float)contentHeight {
  float contentHeight = 0.f;
  
  if (!contentDict_) return 0.f;
  if (contentDict_.count == 0) return 0.f;
  
  for (id content in self.contentDict.objectEnumerator)
  {
    if ([content respondsToSelector:@selector(view)])
          contentHeight += ((UIViewController*)content).view.frame.size.height;
    else contentHeight += ((UIView*)content).frame.size.height;
  }

  return contentHeight;
}

#pragma mark - Touch events

- (void)touchesEnded:(NSSet *)touches withEvent:(UIEvent *)event {
  if (self.arrowView.hidden == NO)
    self.isCollapsed = !isCollapsed_;
}

- (void)userImageTapped:(id)sender {
  UIButton* button = sender;
  Stamp* stamp = [stamps_ objectAtIndex:button.tag];
  
  StampDetailViewController* detailViewController =
  [[StampDetailViewController alloc] initWithStamp:stamp];
  
  StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
  [delegate.navigationController pushViewController:detailViewController animated:YES];
  [detailViewController release];
}


@end
