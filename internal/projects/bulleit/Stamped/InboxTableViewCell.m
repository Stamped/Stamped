//
//  InboxTableViewCell.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/12/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "InboxTableViewCell.h"

#include <math.h>

#import <CoreText/CoreText.h>
#import <QuartzCore/QuartzCore.h>

#import "Entity.h"
#import "Stamp.h"
#import "User.h"
#import "Util.h"
#import "MediumUserImageView.h"
#import "MediumUserImageButton.h"
#import "StampDetailViewController.h"
#import "StampedAppDelegate.h"
#import "UIColor+Stamped.h"

NSString* const kInboxTableDidScrollNotification = @"InboxTableDidScrollNotification";

static NSString* const kTitleFontString = @"TGLight";
static const CGFloat kTitleFontSize = 47.0;
static NSString* const kUserNameFontString = @"Helvetica-Bold";
static NSString* const kCommentFontString = @"Helvetica";
static const CGFloat kSubstringFontSize = 12.0;
static const CGFloat kUserImageHorizontalMargin = 14.0;
static const CGFloat kUserImageSize = 41.0;
static const CGFloat kCellTopPadding = 10.0;
static const CGFloat kSubstringMaxWidth = 218.0;
static const CGFloat kStampSize = 18.0;
static const CGFloat kTitleMaxWidth = 210.0;
static const CGFloat kImageRotations[] = {0.09, -0.08, 0.08, -0.09};

@interface InboxCellView : UIView {
 @private
  // Managed by the top-level view system.
  UIImageView* disclosureImageView_;
  UIImageView* cameraImageView_;
  UIImageView* commentBubbleImageView_;
  UILabel* userNameLabel_;
  UILabel* commentLabel_;
  UILabel* numCommentsLabel_;
  MediumUserImageView* topUserImageView_;
  MediumUserImageView* middleUserImageView_;
  MediumUserImageView* bottomUserImageView_;

  // NOT managed. Must manage ownership.
  CATextLayer* titleLayer_;
  CTFontRef titleFont_;
  CTParagraphStyleRef titleStyle_;
  NSMutableDictionary* titleAttributes_;
  CGRect stampImageFrame_;
  CGFloat userImageRightMargin_;
}

- (CGAffineTransform)transformForUserImageAtIndex:(NSUInteger)index;

// This is magic with UITableViewCell. No need to set this explicitly.
@property (nonatomic, assign, getter=isHighlighted) BOOL highlighted;
@property (nonatomic, assign) BOOL selected;
@property (nonatomic, assign) BOOL hidePhotos;
@property (nonatomic, assign) NSUInteger numComments;
@property (nonatomic, retain) UIImage* stampImage;
@property (nonatomic, copy) NSString* title;
@property (nonatomic, copy) NSArray* stamps;

@property (nonatomic, readonly) UILabel* subtitleLabel;
@property (nonatomic, readonly) UIImageView* typeImageView;

@end

@interface InboxCellView ()
- (NSAttributedString*)titleAttributedStringWithColor:(UIColor*)color;
- (void)invertColors:(BOOL)inverted;
- (void)setSelected:(BOOL)selected animated:(BOOL)animated;
- (void)stampChanged:(NSNotification*)notification;
@end

@implementation InboxCellView

@synthesize highlighted = highlighted_;
@synthesize selected = selected_;
@synthesize numComments = numComments_;
@synthesize stampImage = stampImage_;
@synthesize title = title_;
@synthesize stamps = stamps_;
@synthesize hidePhotos = hidePhotos_;
@synthesize subtitleLabel = subtitleLabel_;
@synthesize typeImageView = typeImageView_;

- (id)initWithFrame:(CGRect)frame {
  self = [super initWithFrame:frame];
  if (self) {
    self.opaque = YES;
    self.backgroundColor = [UIColor whiteColor];
    self.autoresizingMask = UIViewAutoresizingFlexibleHeight;
    
    userImageRightMargin_ = kUserImageSize + (kUserImageHorizontalMargin * 2.0);
    
    typeImageView_ = [[UIImageView alloc] initWithFrame:CGRectMake(userImageRightMargin_, 74, 15, 12)];
    typeImageView_.contentMode = UIViewContentModeBottomLeft;
    [self addSubview:typeImageView_];
    [typeImageView_ release];
    
    subtitleLabel_ = [[UILabel alloc] initWithFrame:CGRectMake(CGRectGetMaxX(typeImageView_.frame) + 4,
                                                               CGRectGetMinY(typeImageView_.frame) + 1, 
                                                               175,
                                                               CGRectGetHeight(typeImageView_.frame))];
    subtitleLabel_.textColor = [UIColor stampedLightGrayColor];
    subtitleLabel_.highlightedTextColor = [UIColor whiteColor];
    subtitleLabel_.font = [UIFont fontWithName:@"Helvetica" size:10];
    [self addSubview:subtitleLabel_];
    [subtitleLabel_ release];

    cameraImageView_ = [[UIImageView alloc] initWithFrame:CGRectMake(293, 34, 17, 14)];
    cameraImageView_.contentMode = UIViewContentModeCenter;
    UIImage* photoIconImage = [UIImage imageNamed:@"inbox_photo_icon"];
    cameraImageView_.image = photoIconImage;
    cameraImageView_.highlightedImage = [Util whiteMaskedImageUsingImage:photoIconImage];
    [self addSubview:cameraImageView_];
    [cameraImageView_ release];
    
    disclosureImageView_ = [[UIImageView alloc] initWithFrame:CGRectMake(300, 37, 8, 11)];
    disclosureImageView_.contentMode = UIViewContentModeScaleAspectFit;
    UIImage* disclosureArrowImage = [UIImage imageNamed:@"disclosure_arrow"];
    disclosureImageView_.image = disclosureArrowImage;
    disclosureImageView_.highlightedImage = [Util whiteMaskedImageUsingImage:disclosureArrowImage];
    [self addSubview:disclosureImageView_];
    [disclosureImageView_ release];
    
    userNameLabel_ = [[UILabel alloc] initWithFrame:CGRectZero];
    userNameLabel_.lineBreakMode = UILineBreakModeTailTruncation;
    userNameLabel_.textColor = [UIColor stampedGrayColor];
    userNameLabel_.highlightedTextColor = [UIColor whiteColor];
    userNameLabel_.font = [UIFont fontWithName:kUserNameFontString size:kSubstringFontSize];
    [self addSubview:userNameLabel_];
    [userNameLabel_ release];
    
    commentLabel_ = [[UILabel alloc] initWithFrame:CGRectZero];
    commentLabel_.font = [UIFont fontWithName:kCommentFontString size:kSubstringFontSize];
    commentLabel_.textColor = [UIColor stampedGrayColor];
    commentLabel_.highlightedTextColor = [UIColor whiteColor];
    [self addSubview:commentLabel_];
    [commentLabel_ release];

    UIImage* bubbleImage = [UIImage imageNamed:@"inbox_chat_bubble"];
    commentBubbleImageView_ = [[UIImageView alloc] initWithImage:bubbleImage
                                                highlightedImage:[Util whiteMaskedImageUsingImage:bubbleImage]];
    commentBubbleImageView_.contentMode = UIViewContentModeCenter;
    [self addSubview:commentBubbleImageView_];
    [commentBubbleImageView_ release];
    
    numCommentsLabel_ = [[UILabel alloc] initWithFrame:CGRectZero];
    numCommentsLabel_.font = [UIFont fontWithName:@"Helvetica" size:10];
    numCommentsLabel_.textAlignment = UITextAlignmentRight;
    numCommentsLabel_.textColor = [UIColor stampedGrayColor];
    numCommentsLabel_.highlightedTextColor = [UIColor whiteColor];
    [self addSubview:numCommentsLabel_];
    [numCommentsLabel_ release];
    
    titleLayer_ = [[CATextLayer alloc] init];
    titleLayer_.truncationMode = kCATruncationEnd;
    titleLayer_.contentsScale = [[UIScreen mainScreen] scale];
    titleLayer_.foregroundColor = [UIColor stampedDarkGrayColor].CGColor;
    titleLayer_.fontSize = 24.0;
    titleLayer_.frame = CGRectMake(userImageRightMargin_, kCellTopPadding, kTitleMaxWidth, kTitleFontSize);
    titleFont_ = CTFontCreateWithName((CFStringRef)kTitleFontString, kTitleFontSize, NULL);
    CFIndex numSettings = 1;
    CTLineBreakMode lineBreakMode = kCTLineBreakByTruncatingTail;
    CTParagraphStyleSetting settings[1] = {
      {kCTParagraphStyleSpecifierLineBreakMode, sizeof(lineBreakMode), &lineBreakMode}
    };
    titleStyle_ = CTParagraphStyleCreate(settings, numSettings);
    titleAttributes_ = [[NSMutableDictionary alloc] initWithObjectsAndKeys:
        (id)titleFont_, (id)kCTFontAttributeName,
        (id)[UIColor stampedDarkGrayColor].CGColor, (id)kCTForegroundColorAttributeName,
        (id)titleStyle_, (id)kCTParagraphStyleAttributeName,
        (id)[NSNumber numberWithDouble:1.2], (id)kCTKernAttributeName, nil];
    CGRect userImgFrame = CGRectMake(kUserImageHorizontalMargin, kCellTopPadding - 1, kUserImageSize, kUserImageSize);
    bottomUserImageView_ = [[MediumUserImageView alloc] initWithFrame:userImgFrame];
    [self addSubview:bottomUserImageView_];
    [bottomUserImageView_ release];
    middleUserImageView_ = [[MediumUserImageView alloc] initWithFrame:userImgFrame];
    [self addSubview:middleUserImageView_];
    [middleUserImageView_ release];
    topUserImageView_ = [[MediumUserImageView alloc] initWithFrame:userImgFrame];
    [self addSubview:topUserImageView_];
    [topUserImageView_ release];
  }
  return self;
}

- (void)dealloc {
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  self.stampImage = nil;
  self.stamps = nil;
  [titleAttributes_ release];
  [titleLayer_ release];
  CFRelease(titleFont_);
  CFRelease(titleStyle_);
  [super dealloc];
}

- (void)invertColors:(BOOL)inverted {
  UIColor* titleColor = [UIColor stampedDarkGrayColor];
  UIColor* badgeColor = [UIColor lightGrayColor];
  if (inverted) {
    titleColor = [UIColor whiteColor];
    badgeColor = [UIColor whiteColor];
  }
  [CATransaction begin];
  [CATransaction setValue:(id)kCFBooleanTrue forKey:kCATransactionDisableActions];
  titleLayer_.string = [self titleAttributedStringWithColor:titleColor];
  titleLayer_.foregroundColor = titleColor.CGColor;
  [CATransaction commit];
  [self setNeedsDisplay];
}

- (CGAffineTransform)transformForUserImageAtIndex:(NSUInteger)index {
  NSUInteger stampsCount = stamps_.count;
  CGAffineTransform transform = CGAffineTransformIdentity;
  if (index >= MAX((NSInteger)stampsCount - 3, 0) && index < stampsCount - 1) {
    transform = CGAffineTransformRotate(
        CGAffineTransformMakeTranslation(0, 4 * ((stampsCount - 1) - index)),
        kImageRotations[index % 4]);
  }
  return transform;
}

- (void)setSelected:(BOOL)selected animated:(BOOL)animated {
  selected_ = selected;
  [self invertColors:selected];
}

- (void)setHighlighted:(BOOL)highlighted {
  highlighted_ = highlighted;
  [self invertColors:highlighted];
}

- (void)drawRect:(CGRect)rect {
  [super drawRect:rect];
  CGContextRef ctx = UIGraphicsGetCurrentContext();
  CGContextSaveGState(ctx);
  CGContextTranslateCTM(ctx, titleLayer_.frame.origin.x, titleLayer_.frame.origin.y);
  [titleLayer_ drawInContext:ctx];
  CGContextRestoreGState(ctx);
  [stampImage_ drawInRect:stampImageFrame_ blendMode:kCGBlendModeMultiply alpha:1.0];
}

- (NSAttributedString*)titleAttributedStringWithColor:(UIColor*)color {
  [titleAttributes_ setObject:(id)color.CGColor forKey:(id)kCTForegroundColorAttributeName];
  NSAttributedString* titleAttributedString = [[NSAttributedString alloc] initWithString:title_
                                                                              attributes:titleAttributes_];
  return [titleAttributedString autorelease];
}

- (void)setTitle:(NSString*)title {
  if (title_ != title) {
    title_ = [title copy];

    NSAttributedString* attrString = [self titleAttributedStringWithColor:[UIColor stampedDarkGrayColor]];
    titleLayer_.string = attrString;
    CTLineRef line = CTLineCreateWithAttributedString((CFAttributedStringRef)attrString);
    CGFloat ascent, descent, leading, width;
    width = fmin(kTitleMaxWidth, CTLineGetTypographicBounds(line, &ascent, &descent, &leading));
    CFRelease(line);
    CGRect oldFrame = stampImageFrame_;
    stampImageFrame_ = CGRectMake(userImageRightMargin_ + width - (kStampSize / 2.0),
                                  kStampSize / 2.0,
                                  kStampSize,
                                  kStampSize);
    [self setNeedsDisplayInRect:oldFrame];
    [self setNeedsDisplayInRect:stampImageFrame_];
    [self setNeedsDisplayInRect:titleLayer_.frame];
  }
}

- (void)setNumComments:(NSUInteger)numComments {
  numComments_ = numComments;
  numCommentsLabel_.hidden = (numComments_ == 0);
  commentBubbleImageView_.hidden = numCommentsLabel_.hidden;
  numCommentsLabel_.text = [NSString stringWithFormat:@"%u", numComments];
  [numCommentsLabel_ sizeToFit];
  if (numComments_ > 0) {
    numCommentsLabel_.frame = CGRectMake(283 - CGRectGetWidth(numCommentsLabel_.frame),
                                         58,
                                         CGRectGetWidth(numCommentsLabel_.frame),
                                         CGRectGetHeight(numCommentsLabel_.frame));
    commentBubbleImageView_.frame = CGRectMake(CGRectGetMinX(numCommentsLabel_.frame) - CGRectGetWidth(commentBubbleImageView_.frame) - 3,
                                               60,
                                               CGRectGetWidth(commentBubbleImageView_.frame),
                                               CGRectGetHeight(commentBubbleImageView_.frame));
  }
  [self setNeedsDisplay];
}

- (void)setStamps:(NSArray*)stamps {
  if (stamps_ == stamps)
    return;

  stamps_ = [stamps copy];
  Stamp* stamp = [stamps_ lastObject];
  //NSLog(@"%@", [Util userReadableTimeSinceDate:stamp.created]);
  
  cameraImageView_.hidden = stamp.imageURL ? NO : YES;
  disclosureImageView_.hidden = !cameraImageView_.hidden;

  self.stampImage = stamp.user.stampImage;
  userNameLabel_.text = stamp.user.screenName;
  [userNameLabel_ sizeToFit];
  userNameLabel_.frame = CGRectMake(userImageRightMargin_,
                                    57,
                                    CGRectGetWidth(userNameLabel_.frame),
                                    CGRectGetHeight(userNameLabel_.frame));

  NSString* comment = stamp.blurb.length ?
      [NSString stringWithFormat:@"\u201c%@\u201d", stamp.blurb] : @"stamped";
  
  self.numComments = [stamp.numComments unsignedIntegerValue];

  CGFloat commentMaxWidth = kSubstringMaxWidth - CGRectGetWidth(userNameLabel_.frame) - 3;
  if (numComments_ > 0)
    commentMaxWidth -= (CGRectGetWidth(numCommentsLabel_.frame) + CGRectGetWidth(commentBubbleImageView_.frame) + 8);

  CGSize stringSize = [comment sizeWithFont:[UIFont fontWithName:kCommentFontString size:kSubstringFontSize]
                                   forWidth:commentMaxWidth
                              lineBreakMode:UILineBreakModeTailTruncation];
  commentLabel_.text = comment;
  commentLabel_.frame = CGRectMake(CGRectGetMaxX(userNameLabel_.frame) + 3,
                                   57,
                                   stringSize.width,
                                   stringSize.height);

  self.hidePhotos = NO;
  
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  for (Stamp* s in stamps_) {
    [[NSNotificationCenter defaultCenter] addObserver:self
                                             selector:@selector(stampChanged:)
                                                 name:kStampDidChangeNotification
                                               object:s];
  }
}

- (void)setHidePhotos:(BOOL)hidePhotos {
  hidePhotos_ = hidePhotos;
  if (hidePhotos) {
    topUserImageView_.hidden = YES;
    middleUserImageView_.hidden = YES;
    bottomUserImageView_.hidden = YES;
    return;
  }
  
  NSUInteger i = 0;
  Stamp* stamp = nil;
  if (stamps_.count == 1) {
    bottomUserImageView_.hidden = YES;
    middleUserImageView_.hidden = YES;
  }
  if (stamps_.count > 1) {
    bottomUserImageView_.hidden = stamps_.count == 2;
    i = stamps_.count - 2;
    stamp = [stamps_ objectAtIndex:i];
    middleUserImageView_.hidden = NO;
    middleUserImageView_.imageURL = stamp.user.profileImageURL;
    middleUserImageView_.transform = [self transformForUserImageAtIndex:i];
  }
  if (stamps_.count > 2) {
    i = stamps_.count - 3;
    stamp = [stamps_ objectAtIndex:i];
    bottomUserImageView_.hidden = NO;
    bottomUserImageView_.imageURL = stamp.user.profileImageURL;
    bottomUserImageView_.transform = [self transformForUserImageAtIndex:i];
  }
  stamp = [stamps_ lastObject];
  topUserImageView_.imageURL = stamp.user.profileImageURL;
  topUserImageView_.hidden = NO;
}

- (void)stampChanged:(NSNotification*)notification {
  // Comments may have changed...
  Stamp* stamp = [notification object];
  self.numComments = [stamp.numComments unsignedIntegerValue];
}

@end


@interface PageDotsView : UIView
@property (nonatomic, assign) NSUInteger numDots;
@property (nonatomic, assign) NSUInteger selectedPage;
@property (nonatomic, assign) BOOL enabled;
@end

@implementation PageDotsView

@synthesize numDots = numDots_;
@synthesize selectedPage = selectedPage_;
@synthesize enabled = enabled_;

- (id)initWithFrame:(CGRect)frame {
  self = [super initWithFrame:frame];
  if (self) {
    self.backgroundColor = [UIColor clearColor];
  }
  return self;
}

- (void)drawRect:(CGRect)rect {
  if (numDots_ == 0)
    return;

  CGContextRef ctx = UIGraphicsGetCurrentContext();
  CGRect dotFrame = CGRectMake(CGRectGetMidX(self.bounds), CGRectGetMidY(self.bounds), 3, 3);
  NSInteger n = -1;
  CGColorRef selectedColor = [UIColor colorWithWhite:0.35 alpha:1.0].CGColor;
  CGColorRef defaultColor = [UIColor colorWithWhite:0.75 alpha:1.0].CGColor;
  for (NSUInteger i = 0; i < numDots_; ++i) {
    NSInteger offset = i > 0 ? 6 * (-1 * n) : 0;
    offset += (numDots_ % 2) == 0 ? 3 : 0;
    NSInteger pageNum = 1;
    if (numDots_ == 2) {
      pageNum = offset < 0 ? 1 : 2;
    } else if (numDots_ == 3) {
      pageNum = offset > 0 ? 3 : offset == 0 ? 2 : 1;
    }
    if (enabled_ && pageNum == selectedPage_) {
      CGContextSetFillColorWithColor(ctx, selectedColor);
    } else {
      CGContextSetFillColorWithColor(ctx, defaultColor);
    }
    CGContextFillEllipseInRect(ctx, CGRectOffset(dotFrame, offset, 0));
    n *= -1;
  }
}

@end


@interface InboxTableViewCell ()
- (void)expandStack;
- (void)collapseStack;
- (void)collapseButtonTapped:(id)sender;
- (void)inboxTableDidScroll:(NSNotification*)notification;
- (void)userImageTapped:(id)sender;
@end

@implementation InboxTableViewCell

@synthesize entityObject = entityObject_;
@synthesize stamp = stamp_;
@synthesize customView = customView_;

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier {
  self = [super initWithStyle:UITableViewCellStyleDefault
              reuseIdentifier:reuseIdentifier];
  if (self) {
    self.accessoryType = UITableViewCellAccessoryNone;
    CGRect customViewFrame = CGRectMake(0, 0, self.contentView.bounds.size.width,
                                              self.contentView.bounds.size.height);
		customView_ = [[InboxCellView alloc] initWithFrame:customViewFrame];
		[self.contentView addSubview:customView_];
    [customView_ release];

    stacksBackgroundView_ = [[UIView alloc] initWithFrame:customViewFrame];
    stacksBackgroundView_.autoresizingMask = UIViewAutoresizingFlexibleWidth |
                                             UIViewAutoresizingFlexibleHeight;
    stacksBackgroundView_.backgroundColor = [UIColor colorWithWhite:0.93 alpha:1.0];
    stacksBackgroundView_.alpha = 0.0;
    [self.contentView addSubview:stacksBackgroundView_];
    [stacksBackgroundView_ release];
    
    stackCollapseButton_ = [UIButton buttonWithType:UIButtonTypeCustom];
    stackCollapseButton_.frame = CGRectMake(11, 7, 46, 46);
    [stackCollapseButton_ setImage:[UIImage imageNamed:@"stacks_back_button"]
                          forState:UIControlStateNormal];
    stackCollapseButton_.alpha = 0.0;
    [stackCollapseButton_ addTarget:self
                             action:@selector(collapseButtonTapped:)
                   forControlEvents:UIControlEventTouchUpInside];
    [self.contentView addSubview:stackCollapseButton_];
    userImageScrollView_ = [[UIScrollView alloc] initWithFrame:CGRectMake(60, 0, 249, 63)];
    userImageScrollView_.alwaysBounceHorizontal = YES;
    userImageScrollView_.pagingEnabled = YES;
    userImageScrollView_.backgroundColor = [UIColor clearColor];
    userImageScrollView_.hidden = YES;
    userImageScrollView_.delegate = self;
    userImageScrollView_.showsHorizontalScrollIndicator = NO;
    [self.contentView addSubview:userImageScrollView_];
    [userImageScrollView_ release];
    
    pageDotsView_ = [[PageDotsView alloc] initWithFrame:CGRectMake(22, 61, 20, 6)];
    pageDotsView_.numDots = 1;
    [self.contentView addSubview:pageDotsView_];
    [pageDotsView_ release];
  }
  return self;
}

- (void)dealloc {
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  self.entityObject = nil;
  userImageScrollView_.delegate = nil;
  [super dealloc];
}

- (void)setSelected:(BOOL)selected animated:(BOOL)animated {
  [super setSelected:selected animated:animated];
  [customView_ setSelected:selected animated:animated];
}

- (void)setStamp:(Stamp*)stamp {
  if (stamp_ != stamp) {
    [stamp_ release];
    stamp_ = [stamp retain];
    if (stamp) {
      customView_.title = stamp.entityObject.title;
      customView_.typeImageView.image = stamp.entityObject.categoryImage;
      customView_.typeImageView.highlightedImage =
          [Util whiteMaskedImageUsingImage:stamp.entityObject.categoryImage];
      customView_.subtitleLabel.text = stamp.entityObject.subtitle;
      customView_.stamps = [NSArray arrayWithObject:stamp];
      pageDotsView_.numDots = 0;
      [self setNeedsDisplay];
    }
  }
}

- (void)setEntityObject:(Entity*)entityObject {
  if (entityObject != entityObject_) {
    [entityObject_ release];
    entityObject_ = [entityObject retain];
  }

  if (entityObject) {
    [self collapseStack];
    customView_.title = entityObject.title;
    customView_.typeImageView.image = entityObject.categoryImage;
    customView_.typeImageView.highlightedImage = [Util whiteMaskedImageUsingImage:entityObject.categoryImage];
    customView_.subtitleLabel.text = entityObject.subtitle;
    NSSortDescriptor* desc = [NSSortDescriptor sortDescriptorWithKey:@"created" ascending:YES];
    NSArray* stampsArray = [entityObject.stamps sortedArrayUsingDescriptors:[NSArray arrayWithObject:desc]];
    stampsArray = [stampsArray filteredArrayUsingPredicate:[NSPredicate predicateWithFormat:@"temporary == NO"]];
    customView_.stamps = stampsArray;
    [[NSNotificationCenter defaultCenter] removeObserver:self];
    if (customView_.stamps.count > 1) {
      [[NSNotificationCenter defaultCenter] addObserver:self
                                               selector:@selector(inboxTableDidScroll:)
                                                   name:kInboxTableDidScrollNotification
                                                 object:nil];
      pageDotsView_.numDots = MIN(3, ceil(customView_.stamps.count / 5.0));
    } else {
      pageDotsView_.numDots = 0;
    }
    [pageDotsView_ setNeedsDisplay];
    [self setNeedsDisplay];
  }
}

- (void)inboxTableDidScroll:(NSNotification*)notification {
  [self collapseButtonTapped:nil];
}

#pragma mark - Touch Events.

- (void)touchesBegan:(NSSet*)touches withEvent:(UIEvent*)event {
  if (stackExpanded_)
    return;
  
  UITouch* touch = [touches anyObject];
  if (customView_.stamps.count > 1 &&
      CGRectContainsPoint(CGRectMake(0, 0, 63, 63), [touch locationInView:customView_])) {
    return;  // Eat the touch event.
  }
  [super touchesBegan:touches withEvent:event];
}

- (void)touchesCancelled:(NSSet*)touches withEvent:(UIEvent*)event {
  if (stackExpanded_)
    return;

  [super touchesCancelled:touches withEvent:event];
}

- (void)touchesEnded:(NSSet*)touches withEvent:(UIEvent*)event {
  UITouch* touch = [touches anyObject];
  if (stackExpanded_)
    return;
  
  if (customView_.stamps.count > 1 &&
      CGRectContainsPoint(CGRectMake(0, 0, 63, 63), [touch locationInView:customView_])) {
    [self expandStack];
    return;
  }
  [super touchesEnded:touches withEvent:event];
}

- (void)touchesMoved:(NSSet*)touches withEvent:(UIEvent*)event {
  if (stackExpanded_)
    return;

  [super touchesMoved:touches withEvent:event];
}

- (void)collapseButtonTapped:(id)sender {
  [self collapseStack];
}

- (void)collapseStack {
  if (stackExpanded_ == NO)
    return;

  userImageScrollView_.contentOffset = CGPointZero;
  userImageScrollView_.hidden = YES;
  NSUInteger i = 0;
  for (UIView* view in userImageScrollView_.subviews) {
    if (![view isMemberOfClass:[MediumUserImageButton class]] || view == stackCollapseButton_)
      continue;
    
    [self.contentView addSubview:view];
    view.transform = CGAffineTransformTranslate(view.transform, 60, 0);
    ++i;
  }
  NSUInteger stampsCount = [customView_.stamps count];
  [UIView animateWithDuration:0.25
                        delay:0
                      options:UIViewAnimationOptionAllowUserInteraction
                   animations:^{
    customView_.transform = CGAffineTransformIdentity;
    stacksBackgroundView_.alpha = 0;
    stackCollapseButton_.alpha = 0;
    pageDotsView_.transform = CGAffineTransformIdentity;

    NSUInteger i = 0;
    for (UIView* view in self.contentView.subviews) {
      if (![view isMemberOfClass:[MediumUserImageButton class]] || view == stackCollapseButton_)
        continue;
      
      view.transform = [customView_ transformForUserImageAtIndex:i];
      if (stampsCount > 3 && (stampsCount - 1 - i) > 2)
        view.alpha = 0.0;

      ++i;
    }
  } completion:^(BOOL finished) {
    customView_.hidePhotos = NO;
    pageDotsView_.enabled = NO;
    [pageDotsView_ setNeedsDisplay];

    self.selectionStyle = UITableViewCellSelectionStyleBlue;
    stackExpanded_ = NO;
    for (UIView* view in self.contentView.subviews) {
      if (![view isMemberOfClass:[MediumUserImageButton class]] || view == stackCollapseButton_)
        continue;
      [view removeFromSuperview];
    }
    [customView_ setNeedsDisplay];
    [self.contentView setNeedsDisplay];
    [stackCollapseButton_ setNeedsDisplay];
  }];
}

- (void)expandStack {
  [self setSelected:NO animated:NO];
  [self setHighlighted:NO animated:NO];
  if (stackExpanded_)
    return;

  stackExpanded_ = YES;
  userImageScrollView_.hidden = NO;
  self.selectionStyle = UITableViewCellSelectionStyleNone;
  CGRect userImgFrame = CGRectMake(kUserImageHorizontalMargin,
                                   kCellTopPadding - 1,
                                   kUserImageSize,
                                   kUserImageSize);
  NSUInteger stampsCount = [customView_.stamps count];
  Stamp* s = nil;
  for (NSUInteger i = 0; i < stampsCount; ++i) {
    s = [customView_.stamps objectAtIndex:i];
    MediumUserImageButton* userImageButton = [[MediumUserImageButton alloc] initWithFrame:CGRectInset(userImgFrame, -2, -2)];
    userImageButton.contentMode = UIViewContentModeCenter;
    userImageButton.layer.shadowOffset = CGSizeZero;
    userImageButton.layer.shadowOpacity = 0.4;
    userImageButton.layer.shadowRadius = 1.0;
    userImageButton.layer.shadowPath = [UIBezierPath bezierPathWithRect:
        CGRectMake(2, 2, CGRectGetWidth(userImgFrame), CGRectGetHeight(userImgFrame))].CGPath;
    userImageButton.imageURL = s.user.profileImageURL;
    
    [userImageButton addTarget:self
                        action:@selector(userImageTapped:)
              forControlEvents:UIControlEventTouchUpInside];
    userImageButton.transform = [customView_ transformForUserImageAtIndex:i];
    userImageButton.tag = i;
    [self.contentView addSubview:userImageButton];
    [userImageButton release];
  }
  customView_.hidePhotos = YES;
  [customView_ setNeedsDisplay];
  [UIView animateWithDuration:0.25 animations:^{
    CGAffineTransform rightTransform =
      CGAffineTransformMakeTranslation(CGRectGetWidth(self.contentView.frame), 0);
    customView_.transform = rightTransform;
    stacksBackgroundView_.alpha = 1.0;
    stackCollapseButton_.alpha = 1.0;
    pageDotsView_.transform = CGAffineTransformMakeTranslation(151, 0);
    
    NSUInteger i = 0;
    for (UIView* view in self.contentView.subviews) {
      if (![view isMemberOfClass:[MediumUserImageButton class]])
        continue;
      
      NSInteger xPos = 55 + (48 * ((stampsCount - 1) - i));
      view.transform = CGAffineTransformMakeTranslation(xPos, 0);
      if (stampsCount > 5 && (stampsCount - 1 - i) > 4)
        view.alpha = 0.0;

      ++i;
    }
  } completion:^(BOOL finished) {
    NSUInteger i = 0;
    NSUInteger numPages = ceil(stampsCount / 5.0);
    NSUInteger pageNum = numPages;
    for (UIView* view in self.contentView.subviews) {
      if (![view isMemberOfClass:[MediumUserImageButton class]])
        continue;

      [userImageScrollView_ addSubview:view];
      NSUInteger count = stampsCount - i;
      if (count != stampsCount && count % 5 == 0)
        --pageNum;
      
      view.transform = CGAffineTransformTranslate(view.transform, -60 + (9 * ((NSInteger)pageNum - 1)), 0);
      if (stampsCount > 5 && count > 5)
        view.alpha = 1.0;

      ++i;
    }
    pageDotsView_.enabled = YES;
    pageDotsView_.selectedPage = 1;
    [pageDotsView_ setNeedsDisplay];
    CGRect scrollBounds = userImageScrollView_.bounds;
    userImageScrollView_.contentSize =
        CGSizeMake(numPages * CGRectGetWidth(scrollBounds), CGRectGetHeight(scrollBounds));
    [self.contentView setNeedsDisplay];
  }];
}

- (void)userImageTapped:(id)sender {
  UIButton* button = sender;
  Stamp* stamp = [customView_.stamps objectAtIndex:button.tag];

  StampDetailViewController* detailViewController =
      [[StampDetailViewController alloc] initWithStamp:stamp];

  StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
  [delegate.navigationController pushViewController:detailViewController animated:YES];
  [detailViewController release];
}


#pragma mark - UIScrollViewDelegate methods.

- (void)scrollViewDidEndDecelerating:(UIScrollView*)scrollView {
  pageDotsView_.selectedPage = (scrollView.contentOffset.x / CGRectGetWidth(scrollView.bounds)) + 1;
  [pageDotsView_ setNeedsDisplay];
}
@end
