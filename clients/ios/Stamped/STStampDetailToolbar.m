//
//  STStampDetailToolbar.m
//  Stamped
//
//  Created by Andrew Bonventre on 3/26/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STStampDetailToolbar.h"

#import "UIColor+Stamped.h"

@interface STStampDetailToolbar ()
- (void)_commonInit;
- (void)_likeButtonPressed:(id)sender;
- (void)_todoButtonPressed:(id)sender;

@property (nonatomic, readonly) UILabel* likeLabel;
@property (nonatomic, readonly) UILabel* todoLabel;
@property (nonatomic, readonly) UILabel* stampLabel;
@property (nonatomic, readonly) UILabel* shareLabel;

@end

@implementation STStampDetailToolbar

@synthesize style = _style;

// All button and subview ownership is managed by the view hierarchy.
@synthesize likeButton = _likeButton;
@synthesize todoButton = _todoButton;
@synthesize stampButton = _stampButton;
@synthesize shareButton = _shareButton;

@synthesize likeLabel = _likeLabel;
@synthesize todoLabel = _todoLabel;
@synthesize stampLabel = _stampLabel;
@synthesize shareLabel = _shareLabel;


- (id)initWithFrame:(CGRect)frame {
  self = [super initWithFrame:frame];
  if (self) {
    [self _commonInit];
  }
  return self;
}

- (id)initWithCoder:(NSCoder*)aDecoder {
  self = [super initWithCoder:aDecoder];
  if (self) {
    [self _commonInit];
  }
  return self;
}

- (void)layoutSubviews {
  [super layoutSubviews];
  _likeLabel.text = _likeButton.selected ? NSLocalizedString(@"Liked", nil) : NSLocalizedString(@"Like", nil);
  _todoLabel.text = _todoButton.selected ? NSLocalizedString(@"To-Do'd", nil) : NSLocalizedString(@"To-Do", nil);

  CGRect buttonFrame = CGRectMake(0, 0, 80, CGRectGetHeight(self.bounds));
  // These two arrays MUST be kept in order.
  NSArray* buttons = nil;
  NSArray* labels = nil;
  if (_style == STStampDetailToolbarStyleDefault) {
    buttons = [NSArray arrayWithObjects:_likeButton, _todoButton, _stampButton, _shareButton, nil];
    labels = [NSArray arrayWithObjects:_likeLabel, _todoLabel, _stampLabel, _shareLabel, nil];
  } else if (_style == STStampDetailToolbarStyleMine) {
    buttons = [NSArray arrayWithObjects:_todoButton, _shareButton, nil];
    labels = [NSArray arrayWithObjects:_todoLabel, _shareLabel, nil];
  }
  NSInteger spacing = CGRectGetWidth(self.bounds) / buttons.count;
  NSInteger xOffset = spacing / 2;
  for (UIButton* b in buttons) {
    b.frame = buttonFrame;
    b.center = CGPointMake(xOffset, b.center.y);
    NSUInteger i = [buttons indexOfObject:b];
    UILabel* l = [labels objectAtIndex:i];
    [l sizeToFit];
    CGRect labelFrame = l.frame;
    labelFrame.origin.x = CGRectGetMidX(b.frame) - CGRectGetMidX(l.bounds);
    labelFrame.origin.y = CGRectGetMaxY(b.frame) - CGRectGetHeight(labelFrame) - 2;
    l.frame = labelFrame;
    xOffset += spacing;
  }
}

- (void)setStyle:(STStampDetailToolbarStyle)style {
  if (style == _style)
    return;

  _style = style;
  [self setNeedsLayout];
}

#pragma mark - Private methods.

- (void)_commonInit {
  _likeButton = [UIButton buttonWithType:UIButtonTypeCustom];
  [_likeButton setImage:[UIImage imageNamed:@"toolbar_likeButton"]
               forState:UIControlStateNormal];
  _likeButton.titleLabel.textColor = [UIColor blackColor];
  [_likeButton setImage:[UIImage imageNamed:@"toolbar_likeButton_highlighted"]
               forState:UIControlStateHighlighted];
  [_likeButton setImage:[UIImage imageNamed:@"toolbar_likeButton_selected"]
               forState:UIControlStateSelected];
  [self addSubview:_likeButton];
  [_likeButton addTarget:self
                  action:@selector(_likeButtonPressed:)
        forControlEvents:UIControlEventTouchUpInside];

  _todoButton = [UIButton buttonWithType:UIButtonTypeCustom];
  [_todoButton setImage:[UIImage imageNamed:@"toolbar_todoButton"]
               forState:UIControlStateNormal];
  [_todoButton setImage:[UIImage imageNamed:@"toolbar_todoButton_highlighted"]
               forState:UIControlStateHighlighted];
  [_todoButton setImage:[UIImage imageNamed:@"toolbar_todoButton_selected"]
               forState:UIControlStateSelected];
  [self addSubview:_todoButton];
  [_todoButton addTarget:self
                  action:@selector(_todoButtonPressed:)
        forControlEvents:UIControlEventTouchUpInside];

  _stampButton = [UIButton buttonWithType:UIButtonTypeCustom];
  [_stampButton setImage:[UIImage imageNamed:@"toolbar_stampButton"]
                forState:UIControlStateNormal];
  [_stampButton setImage:[UIImage imageNamed:@"toolbar_stampButton_highlighted"]
                forState:UIControlStateHighlighted];
  [_stampButton setImage:[UIImage imageNamed:@"toolbar_stampButton_selected"]
                forState:UIControlStateSelected];
  [self addSubview:_stampButton];
  
  _shareButton = [UIButton buttonWithType:UIButtonTypeCustom];
  [_shareButton setImage:[UIImage imageNamed:@"toolbar_shareButton"]
                forState:UIControlStateNormal];
  [_shareButton setImage:[UIImage imageNamed:@"toolbar_shareButton_highlighted"]
                forState:UIControlStateHighlighted];
  [_shareButton setImage:[UIImage imageNamed:@"toolbar_shareButton_selected"]
                forState:UIControlStateSelected];
  [self addSubview:_shareButton];
  
  _likeLabel = [[[UILabel alloc] init] autorelease];
  _likeLabel.text = NSLocalizedString(@"Like", nil);
  _todoLabel = [[[UILabel alloc] init] autorelease];
  _todoLabel.text = NSLocalizedString(@"To-Do", nil);
  _stampLabel = [[[UILabel alloc] init] autorelease];
  _stampLabel.text = NSLocalizedString(@"Stamp", nil);
  _shareLabel = [[[UILabel alloc] init] autorelease];
  _shareLabel.text = NSLocalizedString(@"Share", nil);
  NSArray* labels = [NSArray arrayWithObjects:_likeLabel, _todoLabel, _stampLabel, _shareLabel, nil];
  for (UILabel* l in labels) {
    l.backgroundColor = [UIColor clearColor];
    l.textAlignment = UITextAlignmentCenter;
    l.textColor = [UIColor stampedGrayColor];
    l.font = [UIFont boldSystemFontOfSize:10];
    [self addSubview:l];
  }
}

- (void)_likeButtonPressed:(id)sender {
  _likeButton.selected = !_likeButton.selected;
  [self setNeedsLayout];
}

- (void)_todoButtonPressed:(id)sender {
  _todoButton.selected = !_todoButton.selected;
  [self setNeedsLayout];
}

@end
