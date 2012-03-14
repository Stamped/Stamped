//
//  STActionsViewFactory.m
//  Stamped
//
//  Created by Landon Judkins on 3/13/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STActionsViewFactory.h"
#import <QuartzCore/QuartzCore.h>
#import "STImageView.h"
#import "Util.h"
#import "STViewContainer.h"

@interface ActionItemView : UIView

- (id)initWithAction:(id<STAction>)action andFrame:(CGRect)frame delegate:(id<STViewDelegate>)delegate;
- (void)selected:(id)button;

@property (nonatomic, readonly) id<STViewDelegate> delegate;
@property (nonatomic, readonly) id<STAction> action;

@end

@implementation ActionItemView

@synthesize delegate = delegate_;
@synthesize action = action_;


/*
 TODO
 Check Font
 
 */
- (id)initWithAction:(id<STAction>)action andFrame:(CGRect)frame delegate:(id<STViewDelegate>)delegate {
  self = [super initWithFrame:frame];
  if (self) {
    NSLog(@"loading action: %@",action.name);
    delegate_ = [delegate retain];
    action_ = [action retain];
    self.backgroundColor = [UIColor clearColor];
    CGRect buttonFrame = frame;
    buttonFrame.origin.x = 0;
    buttonFrame.origin.y = 0;
    UIButton* actionView = [[UIButton alloc] initWithFrame:buttonFrame];
    [actionView addTarget:self action:@selector(selected:) forControlEvents:UIControlEventTouchUpInside];
    //actionView.backgroundColor = [UIColor blueColor];
    actionView.backgroundColor = [UIColor clearColor];
    
    self.layer.cornerRadius = 2.0;
    self.layer.borderColor =[UIColor colorWithRed:.8 green:.8 blue:.8 alpha:.4].CGColor;
    self.layer.borderWidth = 1.0;
    self.layer.shadowColor = [UIColor blackColor].CGColor;
    self.layer.shadowOpacity = .05;
    self.layer.shadowRadius = 1.0;
    self.layer.shadowOffset = CGSizeMake(0, 1);
    
    CAGradientLayer* gradient = [CAGradientLayer layer];
    gradient.anchorPoint = CGPointMake(0, 0);
    gradient.position = CGPointMake(0, 0);
    gradient.bounds = actionView.layer.bounds;
    gradient.cornerRadius = 2.0;
    gradient.colors = [NSMutableArray arrayWithObjects:
                       (id)[UIColor colorWithRed:1.0 green:1.0 blue:1.0 alpha:.8].CGColor,
                       (id)[UIColor colorWithRed:.95 green:.95 blue:.95 alpha:.6].CGColor,
                       nil];
    [self.layer addSublayer:gradient];
    
    CGRect labelFrame = frame;
    labelFrame.size.width = 200;
    labelFrame.origin.x = 44;
    labelFrame.origin.y = 0;
    
    UILabel* label = [[UILabel alloc] initWithFrame:labelFrame];
    label.text = action.name;
    CGFloat greyTone = .35;
    label.textColor = [UIColor colorWithRed:greyTone green:greyTone blue:greyTone alpha:1.0];
    label.font = [UIFont fontWithName:@"Helvetica-Bold" size:12];
    label.backgroundColor = [UIColor clearColor];
    label.textAlignment = UITextAlignmentLeft;
    [self addSubview:label];
    [self addSubview:actionView];
    [actionView release];
    [label release];
    
    CGRect imageFrame = CGRectMake(12, 12, 20, 20);
    UIView* imageView = [Util imageViewWithURL:[NSURL URLWithString:action.icon] andFrame:imageFrame];
    [self addSubview:imageView];
    if (action.sources) {
      NSInteger index = [action.sources count] - 1;
      CGFloat offset = frame.size.width - 32;
      while (index >= 0) {
        id<STSource> source = [action.sources objectAtIndex:index];
        if (source.icon) {
          CGRect iconFrame = CGRectMake(offset, 14, 16, 16);
          UIView* iconView = [Util imageViewWithURL:[NSURL URLWithString:source.icon] andFrame:iconFrame];
          [self addSubview:iconView];
          offset -= 20;
        }
        index--;
      }
    }
  }
  return self;
}

- (void)selected:(id)button {
  NSLog(@"selected %@ %@",self.action.name, self.action.icon);
  CGFloat delta = 25;
  if (self.frame.size.height > 20) {
    delta = -25;
  }
  [self.delegate view:self willChangeHeightBy:delta over:.25];
}

- (void)drawRect:(CGRect)rect {
  [super drawRect:rect];
}

@end

@implementation STActionsViewFactory

- (void)createWithActions:(NSArray<STAction>*)actions
                 delegate:(id<STViewDelegate>)delegate
                withLabel:(id)label {
  STViewContainer* view = nil;
  if (actions) {
    view = [[STViewContainer alloc] initWithFrame:CGRectMake(0, 0, 320, 10)];
    view.delegate = delegate;
    //view.backgroundColor = [UIColor redColor];
    CGFloat cell_height = 44;
    CGFloat cell_padding_h = 5;
    CGFloat cell_width = 290;
    CGFloat cell_padding_w = (320 - cell_width) / 2.0;
    for (id<STAction> action in actions) {
      CGRect frame = CGRectMake(cell_padding_w, 0, cell_width, cell_height);
      UIView* actionView = [[ActionItemView alloc] initWithAction:action andFrame:frame delegate:view]; 
      [view appendChild:actionView];
      [actionView release];
      CGRect viewFrame = view.frame;
      viewFrame.size.height += cell_padding_h;
      view.frame = viewFrame;
    }
    [view autorelease];
  }
  [delegate didLoad:view withLabel:label];
}

@end
