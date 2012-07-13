  //
//  CollapsibleViewController.m
//  Stamped
//
//  Created by Jake Zien on 9/7/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <QuartzCore/QuartzCore.h>

#import "CollapsibleViewController.h"
#import "PairedLabel.h"
#import "WrappingTextView.h"
#import "UIColor+Stamped.h"
#import "UserImageView.h"
#import "Util.h"


@implementation CollapsibleViewController

@synthesize headerView = headerView_;
@synthesize contentView = contentView_;
@synthesize sectionLabel = sectionLabel_;
@synthesize arrowView = arrowView_;
@synthesize isCollapsed = isCollapsed_;
@synthesize contentDict = contentDict_;
@synthesize numLabel = numLabel_;
@synthesize iconView = iconView_;
@synthesize delegate = delegate_;
@synthesize collapsedHeight = collapsedHeight_;
@synthesize footerView = footerView_;
@synthesize footerLabel = footerLabel_;
@synthesize collapsedFooterText = collapsedFooterText_;
@synthesize expandedFooterText = expandedFooterText_; 
@synthesize imageView = imageView_;
@synthesize stamps = stamps_;
@synthesize isSilent = isSilent_;

static const NSUInteger kLabelHeight = 20;
static const NSUInteger kImageHeight = 40;
static const NSUInteger kSpaceHeight = 10;

- (id)initWithNibName:(NSString*)nibNameOrNil bundle:(NSBundle*)nibBundleOrNil {
  self = [super initWithNibName:nibNameOrNil bundle:nibBundleOrNil];
  if (self) {
    isCollapsed_ = YES;
    collapsedHeight_ = 40.0f;

    if ([nibNameOrNil isEqualToString:@"CollapsiblePreviewController"])
      previewMode_ = YES;

    contentDict_ = [[NSMutableDictionary alloc] init];

    maxNameLabelWidth = 0.f;
  }
  return self;
}

- (void)dealloc {
  self.headerView = nil;
  self.footerView = nil;
  self.contentView = nil;
  self.arrowView = nil;
  self.iconView = nil;
  self.sectionLabel = nil;
  self.numLabel = nil;
  self.footerLabel = nil;
  self.contentDict = nil;
  self.stamps = nil;
  [super dealloc];
}

- (void)didReceiveMemoryWarning {
  // Releases the view if it doesn't have a superview.
  [super didReceiveMemoryWarning];
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  self.arrowView.image = [UIImage imageNamed:@"eDetail-arrow-down"];
  UITapGestureRecognizer* gr = [[UITapGestureRecognizer alloc] initWithTarget:self action:@selector(handleTap:)];
  [self.view addGestureRecognizer:gr];
  [gr release];
  [super viewDidLoad];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  self.headerView = nil;
  self.footerView = nil;
  self.contentView = nil;
  self.arrowView = nil;
  self.iconView = nil;
  self.sectionLabel = nil;
  self.numLabel = nil;
  self.footerLabel = nil;
  self.contentDict = nil;
  self.stamps = nil;
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
  if (delegate_ && [(id)delegate_ respondsToSelector:@selector(callMoveArrowOnCollapsibleViewController:)])
    [self.delegate callMoveArrowOnCollapsibleViewController:self];
}

#pragma mark - Collapsing and expanding

- (void)collapse {
  if (!self.isSilent)
    [self.delegate collapsibleViewController:self 
                          willChangeHeightBy:(collapsedHeight_ - self.view.bounds.size.height)];
  self.view.frame = CGRectMake(self.view.frame.origin.x, self.view.frame.origin.y,
                               self.view.frame.size.width, collapsedHeight_);
  if (self.footerLabel && self.footerLabel.text.length > 0) {
    self.footerLabel.text = self.collapsedFooterText;
    CGFloat delta = CGRectGetMinX(self.footerLabel.frame) + 
      [self.footerLabel.text sizeWithFont:self.footerLabel.font].width - CGRectGetMinX(arrowView_.frame);
    arrowView_.frame = CGRectOffset(arrowView_.frame, delta, 0);
  }
  if (!isCollapsed_)
    isCollapsed_ = YES;
}

- (void)expand {
  CGFloat newHeight = 40.f + [self contentHeight] + kSpaceHeight;
  if (self.footerView)
    newHeight += self.footerView.frame.size.height - (kSpaceHeight * 2);
  if (!self.isSilent)
    [self.delegate collapsibleViewController:self willChangeHeightBy:newHeight - self.view.bounds.size.height];
  self.view.frame = CGRectMake(self.view.frame.origin.x, self.view.frame.origin.y,
                               self.view.frame.size.width, newHeight);
  if (self.footerLabel && ![self.footerLabel.text isEqualToString:@""]) {
    self.footerLabel.text = self.expandedFooterText;
    CGFloat delta = CGRectGetMinX(self.footerLabel.frame) + [self.footerLabel.text sizeWithFont:self.footerLabel.font].width - CGRectGetMinX(arrowView_.frame);
    arrowView_.frame = CGRectOffset(arrowView_.frame, delta, 0);
  }
  if (isCollapsed_)
    isCollapsed_ = NO;
}

- (void)collapseAnimated {
  [UIView animateWithDuration:0.25 
                   animations:^{[self collapse];
                                arrowView_.transform = CGAffineTransformMakeRotation(M_PI);}
                   completion:^(BOOL finished){[self swapArrowImage];}];
}

- (void)expandAnimated {  
  [UIView animateWithDuration:0.25
                   animations:^{[self expand];
                                arrowView_.transform = CGAffineTransformMakeRotation(M_PI);}
                   completion:^(BOOL finished){[self swapArrowImage];}];
}

- (void)setIsCollapsed:(BOOL)collapsed {
  isCollapsed_ = collapsed;
  if (isCollapsed_) {
    [self collapseAnimated];
  } else {
    [self expandAnimated];
  }
}

// So the shadow always comes from the top edge.
- (void)swapArrowImage {
  if (isCollapsed_) {
    arrowView_.transform = CGAffineTransformMakeRotation(0);
    arrowView_.image = [UIImage imageNamed:@"eDetail-arrow-down"]; 
  } else {
    arrowView_.transform = CGAffineTransformMakeRotation(0);
    arrowView_.image = [UIImage imageNamed:@"eDetail-arrow-up"]; 
  }
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
  if (newWidth > maxNameLabelWidth) {
    maxNameLabelWidth = newWidth;
    
    for (UIViewController* vc in self.contentDict.objectEnumerator) {
      if ([vc isKindOfClass:[PairedLabel class]]) {
        ((PairedLabel*)vc).nameWidth = maxNameLabelWidth;
      }                           
    }
  }
  frame.origin = CGPointMake(sectionLabel_.frame.origin.x, [self contentHeight]);
  newLabel.view.frame = frame;
  newLabel.nameWidth = maxNameLabelWidth;
  
  [self addContent:newLabel forKey:key];
  [newLabel release];
}

- (void)addNumberedListWithValues:(NSArray*)values {
  NSUInteger itemNumber = 0;
  for (NSString* value in values) {
    PairedLabel* newLabel = [[PairedLabel alloc] initWithNibName:@"PairedLabel" bundle:nil];
    
    CGRect frame = newLabel.view.frame;
    frame.origin = CGPointMake(sectionLabel_.frame.origin.x, [self contentHeight]);
    frame.size = CGSizeMake(contentView_.frame.size.width, 16.f); 
    newLabel.view.frame = frame;
    
    // Change "label" field font for numbering.
    newLabel.nameLabel.font = [UIFont fontWithName:@"Helvetica-Bold" size:10.f];
    newLabel.nameLabel.textColor = [UIColor stampedLightGrayColor];
    
    newLabel.nameLabel.text = [NSString stringWithFormat:@"%d", ++itemNumber];
    newLabel.valueLabel.text = value;

    CGFloat newWidth = [newLabel.nameLabel.text sizeWithFont:newLabel.nameLabel.font].width;
    if (newWidth > maxNameLabelWidth) {
      maxNameLabelWidth = newWidth;
      
      for (UIViewController* vc in self.contentDict.objectEnumerator) {
        if ([vc isKindOfClass:[PairedLabel class]]) {
          ((PairedLabel*)vc).numberWidth = maxNameLabelWidth;
        }
      }
    }
    frame.origin = CGPointMake(sectionLabel_.frame.origin.x, [self contentHeight]);

    newLabel.view.frame = frame;
    newLabel.numberWidth = maxNameLabelWidth;
    
    [self addContent:newLabel forKey:[NSString stringWithFormat:@"%d", itemNumber]];
    [newLabel release];
  }
  // Ensure that all the items are spaced correctly.
  itemNumber = 1;
  for (NSString* value in values) {
    PairedLabel* itemAbove = [self.contentDict objectForKey:[NSString stringWithFormat:@"%d", itemNumber]];
    PairedLabel* item = [self.contentDict objectForKey:[NSString stringWithFormat:@"%d", ++itemNumber]];
    CGRect frame = item.view.frame;
    frame.origin = CGPointMake(item.view.frame.origin.x, CGRectGetMaxY(itemAbove.view.frame));
    item.view.frame = frame;
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
  [textView release];
  CGRect frame = textView.frame;
  frame.size.height = textView.contentSize.height;
  textView.frame = frame;
}

- (void)addWrappingText:(NSString*)text forKey:(NSString*)key {
  CGRect frame = CGRectMake(15.f, 0.0, contentView_.frame.size.width-30.0, 10.0);
  CGSize previewRectSize = CGSizeMake(0,0);
  
  if (self.imageView && self.imageView.hidden == NO) {
    CGRect imageViewFrame = [self.contentView convertRect:self.imageView.frame fromView:self.imageView.superview];
    previewRectSize = CGSizeMake(CGRectGetMinX(self.imageView.frame) - 20.0, CGRectGetMaxY(imageViewFrame) + 10.0);
  }
  
  WrappingTextView* wrapText = [[WrappingTextView alloc] initWithFrame:frame text:text];
  wrapText.previewRectSize = previewRectSize;
  
  [self addContent:wrapText forKey:key];
  [wrapText release];
}
//
//- (void)addImagesForStamps:(NSSet*)newStamps {
//  NSSortDescriptor* desc = [NSSortDescriptor sortDescriptorWithKey:@"created" ascending:YES];
//  NSArray* stampsArray = [newStamps sortedArrayUsingDescriptors:[NSArray arrayWithObject:desc]];
//  User* currentUser = [AccountManager sharedManager].currentUser;
//  NSSet* following = currentUser.following;
//  if (!following)
//    following = [NSSet set];
//
//  stampsArray = [stampsArray filteredArrayUsingPredicate:[NSPredicate predicateWithFormat:@"(user IN %@ OR user.userID == %@) AND deleted == NO", following, currentUser.userID]];
//
//  [stamps_ release];
//  stamps_ = [stampsArray retain];
//  
//  UIScrollView* scrollView = [[UIScrollView alloc] initWithFrame:contentView_.frame];
//  scrollView.frame = CGRectMake(0.f, 0.f, contentView_.frame.size.width, 58.0);
//  scrollView.userInteractionEnabled = YES;
//  scrollView.bounces = YES;
//  scrollView.contentSize = CGSizeMake(scrollView.frame.size.width + 1.0, scrollView.frame.size.height);
//  scrollView.showsHorizontalScrollIndicator = NO;
//  scrollView.showsVerticalScrollIndicator = NO;
//  scrollView.scrollsToTop = NO;
//  scrollView.pagingEnabled = YES;
//
//  CGRect userImgFrame = CGRectMake(0.0, 0.0, 43.0, 43.0);
//
//  Stamp* s = nil;
//  NSUInteger pageNum = 1;
//  for (NSUInteger i = 0; i < stamps_.count; ++i) {
//    s = [stamps_ objectAtIndex:i];
//    UserImageView* userImage = [[UserImageView alloc] initWithFrame:userImgFrame];
//    
//    if (i > 1 && i % 6 == 0) {
//      scrollView.contentSize = CGSizeMake(scrollView.contentSize.width + scrollView.frame.size.width, scrollView.contentSize.height);
//      pageNum++;
//    }
//    
//    CGFloat xOffset = i * (userImgFrame.size.width + 7.0) + 18.0 * (pageNum - 1) + 14.0;
//    
//    userImage.frame = CGRectOffset(userImgFrame, xOffset, 5);
//    userImage.contentMode = UIViewContentModeCenter;
//    userImage.imageURL = [s.user profileImageURLForSize:ProfileImageSize46];
//    userImage.enabled = YES;
//    [userImage addTarget:self
//                  action:@selector(userImageTapped:)
//        forControlEvents:UIControlEventTouchUpInside];
//    userImage.tag = i;
//    [scrollView addSubview:userImage];
//    [userImage release];
//  }
//  
//  self.numLabel.text = [NSString stringWithFormat:@"(%d)", stamps_.count];
//  self.numLabel.hidden = NO;
//  
//  [self addContent:scrollView forKey:@"stamps"];
//  [scrollView release];
//}

- (void)addContent:(id)content forKey:(NSString*)key {
  [self.contentDict setObject:content forKey:key];
  if ([content respondsToSelector:@selector(view)])
    [contentView_ addSubview:((CollapsibleViewController*)content).view];
  else 
    [contentView_ addSubview:(UIView*)content];
  
  if (self.footerLabel.hidden == NO && self.contentHeight <= self.contentView.frame.size.height) {
    self.footerLabel.hidden = YES;
    self.arrowView.hidden = YES;
    self.collapsedHeight = self.headerView.frame.size.height + self.contentHeight;
    
    CGRect contentFrame = self.contentView.frame;
    contentFrame.size.height +=20;
    self.contentView.frame = contentFrame;
    
    CGRect viewFrame = self.view.frame;
    viewFrame.size.height = CGRectGetMaxY(self.footerView.frame) - 20;
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
    viewFrame.size.height = CGRectGetMaxY(self.footerView.frame) + 20;
    self.view.frame = viewFrame;
  }
}

- (CGFloat)contentHeight {
  CGFloat contentHeight = 0.0f;
  
  if (!contentDict_ || contentDict_.count == 0)
    return 0.f;
  
  for (id content in self.contentDict.objectEnumerator) {
    if ([content respondsToSelector:@selector(view)]) {
      contentHeight += ((UIViewController*)content).view.frame.size.height;
    } else {
      contentHeight += ((UIView*)content).frame.size.height;
    }
  }

  return contentHeight;
}

- (void)moveArrowViewIfBehindImageView:(UIImageView*)imageView {
  if (footerLabel_ && footerLabel_.text && ![footerLabel_.text isEqualToString:@""]) {
    CGRect frame = self.arrowView.frame;
    frame.origin = CGPointMake([self.footerLabel.text sizeWithFont:self.footerLabel.font].width + 15.0, arrowView_.frame.origin.y);
    self.arrowView.frame = frame;
  }
  
  CGRect convertedArrowFrame = [self.view convertRect:self.arrowView.frame toView:self.view];
  CGRect actualImageFrame = [Util frameForImage:imageView.image inImageViewAspectFit:imageView];
  CGSize offset = CGSizeMake(imageView.frame.size.width-actualImageFrame.size.width,
                             imageView.frame.size.height-actualImageFrame.size.height);
  actualImageFrame = CGRectOffset(actualImageFrame, offset.width/2, offset.height/2);
  actualImageFrame = [imageView convertRect:actualImageFrame toView:self.view];

  if (CGRectGetMinY(convertedArrowFrame) >= CGRectGetMinY(actualImageFrame) &&
      CGRectGetMaxY(convertedArrowFrame) - 20 <= CGRectGetMaxY(actualImageFrame)) {
    if (CGRectGetMinX(convertedArrowFrame) >= CGRectGetMinX(actualImageFrame)) {
      CGRect convertedImageFrame = [self.view convertRect:actualImageFrame toView:self.arrowView.superview];
      
      self.arrowView.frame = CGRectMake(CGRectGetMinX(convertedImageFrame) - 42.0,
                                        CGRectGetMinY(self.arrowView.frame), 
                                        CGRectGetWidth(self.arrowView.frame),
                                        CGRectGetHeight(self.arrowView.frame));
    }
  } else {
    CGRect frame = self.arrowView.frame;
    CGPoint origin = frame.origin;
    origin.x = self.view.frame.size.width - frame.size.width;
    frame.origin = origin;
    self.arrowView.frame = frame;
  }
}

#pragma mark - Touches

- (void)handleTap:(id)sender {
  if (self.stamps.count > 0) {
    CGPoint loc = [(UITapGestureRecognizer*)sender locationInView:self.view];
    UIView* subview = [self.view hitTest:loc withEvent:nil];
    if ([subview isKindOfClass:[UserImageView class]]) {
      [self userImageTapped:subview];
      return;
    }
  }
  
  if (self.arrowView.hidden == NO)
    self.isCollapsed = !isCollapsed_;
}
//
//- (void)userImageTapped:(id)sender {
//  UIButton* button = sender;
//  Stamp* stamp = [stamps_ objectAtIndex:button.tag];
//  
//  StampDetailViewController* detailViewController =
//      [[StampDetailViewController alloc] initWithStamp:stamp];
//  UINavigationController* navController = self.navigationController;
//  if (!navController) {
//    StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
//    navController = delegate.navigationController;
//  }
//  [navController pushViewController:detailViewController animated:YES];
//  [detailViewController release];
//}


@end
