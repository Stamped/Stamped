//
//  STMenuPopUp.m
//  Stamped
//
//  Created by Landon Judkins on 3/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STMenuPopUp.h"
#import "Util.h"
#import "UIFont+Stamped.h"
#import "UIColor+Stamped.h"
#import "STViewContainer.h"
#import <QuartzCore/QuartzCore.h>
#import "STImageView.h"
#import "STActionManager.h"
#import "STSimpleSource.h"

@interface STMenuPopUpHeaderGradient : UIView

@end

@interface STMenuPopUpSubmenuHeader : UIView <UIScrollViewDelegate>

- (id)initWithMenu:(id<STMenu>)menu sectionBoundaries:(NSArray*)boundaries andScrollView:(UIScrollView*)scrollView;

@property (nonatomic, readonly, retain) UILabel* label;
@property (nonatomic, readonly, retain) NSArray* boundaries;
@property (nonatomic, readonly, retain) id<STMenu> menu;

@end

@implementation STMenuPopUp

- (void)exitPopUp:(id)object {
  [Util setFullScreenPopUp:nil dismissible:NO withBackground:nil];
}

- (void)attributionButton:(id)object {
  STSimpleSource* source = [[STSimpleSource alloc] init];
  source.link = object;
  [[STActionManager sharedActionManager] didChooseSource:source forAction:nil withContext:[STActionContext context]];
}

- (id)initWithEntityDetail:(id<STEntityDetail>)entityDetail andMenu:(id<STMenu>)menu {
  self = [super init];
  if (self) {
    CGFloat width = 290;
    CGFloat height = 360;
    CGFloat padding = 10;
    self.frame = [Util centeredAndBounded:CGSizeMake(width, height) inFrame:[UIApplication sharedApplication].keyWindow.frame];
    self.backgroundColor = [UIColor whiteColor];
    
    UIImageView* topBar = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:@"popup_wht_top"]] autorelease];
    [self addSubview:topBar];
    
    UIImageView* botBar = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:@"popup_wht_bot"]] autorelease];
    botBar.frame = CGRectOffset(botBar.frame, 0, self.frame.size.height - botBar.frame.size.height);
    [self addSubview:botBar];
    
    UIImageView* exitIcon = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:@"popup_wht_closeButton"]] autorelease];
    exitIcon.frame = CGRectOffset(exitIcon.frame, -exitIcon.frame.size.width/2, -exitIcon.frame.size.height/2);
    [self addSubview:exitIcon];
    CGRect titleFrame = CGRectMake(padding, 0, width - (2 * padding), 50);
    UIView* titleView = [Util viewWithText:entityDetail.title
                                      font:[UIFont stampedTitleFontWithSize:20] 
                                     color:[UIColor stampedDarkGrayColor] 
                                      mode:UILineBreakModeClip 
                                andMaxSize:titleFrame.size];
    titleView.frame = [Util centeredAndBounded:titleView.frame.size inFrame:titleFrame];
    [self addSubview:titleView];
    
    UIView* exitButton = [Util tapViewWithFrame:exitIcon.frame target:self selector:@selector(exitPopUp:) andMessage:nil];
    [self addSubview:exitButton];
    
    STViewContainer* body = [[[STViewContainer alloc] initWithDelegate:nil andFrame:CGRectMake(0, 0, width, 0)] autorelease];
    
    CGRect componentFrame = CGRectMake(padding, 0, width - (2 * padding), CGFLOAT_MAX);
    
    CGFloat sectionTitleSize = 16;
    CGFloat itemTitleSize = 14;
    CGFloat itemDescSize = 12;
    CGFloat itemPriceSize = itemDescSize;
    CGRect tempFrame;
    BOOL firstSection = YES;
    tempFrame = body.frame;
    tempFrame.size.height += 24;
    body.frame = tempFrame;
    NSMutableArray* boundaries = [NSMutableArray array];
    for (id<STSubmenu> submenu in menu.menus) {
      [boundaries addObject:[NSNumber numberWithFloat:body.frame.size.height]];
      for (id<STMenuSection> section in submenu.sections) {
        if (!firstSection) {
          UIImageView* seperator = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:@"popup_menu_dottedLine"]] autorelease];
          componentFrame.size.height = 40;
          seperator.frame = [Util centeredAndBounded:seperator.frame.size inFrame:componentFrame];
          [body appendChildView:seperator];
          tempFrame = body.frame;
          tempFrame.size.height += 20;
          body.frame = tempFrame;
        }
        if (section.title) {
          UILabel* sectionTitle = [Util viewWithText:section.title 
                                                font:[UIFont stampedFontWithSize:sectionTitleSize]
                                               color:[UIColor stampedGrayColor] 
                                                mode:UILineBreakModeWordWrap 
                                          andMaxSize:CGSizeMake(width,CGFLOAT_MAX)];
          sectionTitle.textAlignment = UITextAlignmentCenter;
          componentFrame.size.height = sectionTitle.frame.size.height;
          if (firstSection) {
            componentFrame.size.height += 10;
          }
          sectionTitle.frame = [Util centeredAndBounded:sectionTitle.frame.size inFrame:componentFrame];
          [body appendChildView:sectionTitle];
          tempFrame = body.frame;
          tempFrame.size.height += 20;
          body.frame = tempFrame;
        }
        for (id<STMenuItem> item in section.items) {
          if (item.title) {
            UILabel* itemTitle = [Util viewWithText:item.title 
                                               font:[UIFont stampedBoldFontWithSize:itemTitleSize] 
                                              color:[UIColor stampedDarkGrayColor] 
                                               mode:UILineBreakModeWordWrap 
                                         andMaxSize:CGSizeMake(width, CGFLOAT_MAX)];
            itemTitle.textAlignment = UITextAlignmentCenter;
            componentFrame.size.height = itemTitle.frame.size.height;
            itemTitle.frame = [Util centeredAndBounded:itemTitle.frame.size inFrame:componentFrame];
            [body appendChildView:itemTitle];
          }
          if (item.desc) {
            UILabel* itemDesc = [Util viewWithText:item.desc 
                                              font:[UIFont stampedFontWithSize:itemDescSize] 
                                             color:[UIColor stampedGrayColor] 
                                              mode:UILineBreakModeWordWrap 
                                        andMaxSize:CGSizeMake(width, CGFLOAT_MAX)];
            itemDesc.textAlignment = UITextAlignmentCenter;
            componentFrame.size.height = itemDesc.frame.size.height;
            itemDesc.frame = [Util centeredAndBounded:itemDesc.frame.size inFrame:componentFrame];
            [body appendChildView:itemDesc];
          }
          if ([item.prices count] > 0) {
            NSMutableArray* prices = [NSMutableArray array];
            for (id<STMenuPrice> price in item.prices) {
              if (price.price) {
                NSString* priceString = price.price;
                if (price.currency && [price.currency isEqualToString:@"dollars"]) {
                  priceString = [NSString stringWithFormat:@"$%@", priceString, nil];
                }
                [prices addObject:priceString];
              }
            }
            if ([prices count]) {
              NSString* pricesString = [prices componentsJoinedByString:@" / "];
              UILabel* pricesView = [Util viewWithText:pricesString 
                                                  font:[UIFont stampedFontWithSize:itemPriceSize] 
                                                 color:[UIColor stampedGrayColor] 
                                                  mode:UILineBreakModeWordWrap 
                                            andMaxSize:CGSizeMake(width, CGFLOAT_MAX)];
              pricesView.textAlignment = UITextAlignmentCenter;
              componentFrame.size.height = pricesView.frame.size.height;
              pricesView.frame = [Util centeredAndBounded:pricesView.frame.size inFrame:componentFrame];
              [body appendChildView:pricesView];
            }
          }
          CGRect bodyFrame = body.frame;
          bodyFrame.size.height += 10;
          body.frame = bodyFrame;
        }
        firstSection = NO;
      }
    }
    
    CGRect bodyFrame = CGRectMake(0, titleFrame.size.height, width, height-titleFrame.size.height-35);
    UIScrollView* scrollView = [[[UIScrollView alloc] initWithFrame:bodyFrame] autorelease];
    [scrollView addSubview:body];
    scrollView.contentSize = body.frame.size;
    
    [self addSubview:scrollView];
    
    STMenuPopUpSubmenuHeader* header = [[[STMenuPopUpSubmenuHeader alloc] initWithMenu:menu sectionBoundaries:boundaries andScrollView:scrollView] autorelease];
    tempFrame = header.frame;
    tempFrame.origin.y += titleFrame.size.height;
    header.frame = tempFrame;
    scrollView.delegate = header;
    [self addSubview:header];
    
    CGRect bottonGradientFrame = CGRectMake(0, CGRectGetMaxY(bodyFrame)-30, width, 30);
    CAGradientLayer* gradient = [CAGradientLayer layer];
    gradient.frame = bottonGradientFrame;
    gradient.colors = [NSMutableArray arrayWithObjects:
                       (id)[UIColor colorWithRed:1 green:1 blue:1 alpha:0].CGColor,
                       (id)[UIColor colorWithRed:1 green:1 blue:1 alpha:1].CGColor,
                       nil];
    [self.layer addSublayer:gradient];
    
    if (menu.attributionImage) {
      NSData* data = [NSData dataWithContentsOfURL:[NSURL URLWithString:menu.attributionImage]];
      UIImageView* attributionImage = [[[UIImageView alloc] initWithImage:[UIImage imageWithData:data]] autorelease];
      tempFrame = attributionImage.frame;
      tempFrame.size = CGSizeMake(attributionImage.frame.size.width / [Util imageScale], attributionImage.frame.size.height / [Util imageScale]);
      tempFrame = CGRectMake(width-tempFrame.size.width-padding, 
                                          CGRectGetMaxY(bodyFrame), 
                                          tempFrame.size.width, 
                                          tempFrame.size.height);
      tempFrame.origin.y = height - CGRectGetHeight(tempFrame) - 5;
      tempFrame.origin.x = CGRectGetMaxX(tempFrame) - tempFrame.size.width - 5;
      attributionImage.frame = tempFrame;
      [self addSubview:attributionImage];
      if (menu.attributionImageLink) {
        UIView* attributionButton = [Util tapViewWithFrame:attributionImage.frame target:self selector:@selector(attributionButton:) andMessage:menu.attributionImageLink];
        [self addSubview:attributionButton];
      }
    }
  }
  return self;
}

@end

@implementation STMenuPopUpSubmenuHeader

@synthesize label = _label;
@synthesize boundaries = _boundaries;
@synthesize menu = _menu;

- (id)initWithMenu:(id<STMenu>)menu sectionBoundaries:(NSArray*)boundaries andScrollView:(UIScrollView*)scrollView {
  self = [super initWithFrame:CGRectMake(0, 0, 290, 24)];
  if (self) {
    self.backgroundColor = [UIColor clearColor];
    NSString* initialText = @"";
    if ([menu.menus count] > 0) {
      initialText = [[menu.menus objectAtIndex:0] title];
    }
    _label = [[Util viewWithText:initialText font:[UIFont stampedBoldFontWithSize:14] color:[UIColor stampedGrayColor] mode:UILineBreakModeClip andMaxSize:self.frame.size] retain];
    _label.frame = self.frame;
    _label.textAlignment = UITextAlignmentCenter;
    _boundaries = [boundaries retain];
    _menu = [menu retain];    
    UIView* gradientS = [[[STMenuPopUpHeaderGradient alloc] initWithFrame:CGRectOffset(self.frame, -self.frame.origin.x, -self.frame.origin.y)] autorelease];
    [self scrollViewDidScroll:scrollView];
    CAGradientLayer* gradient = [CAGradientLayer layer];
    gradient.anchorPoint = CGPointMake(0, 0);
    gradient.position = CGPointMake(0, 0);
    gradient.bounds = self.layer.bounds;
    CGFloat gradientShade = .8;
    gradient.colors = [NSMutableArray arrayWithObjects:
                       (id)[UIColor colorWithRed:gradientShade green:gradientShade blue:gradientShade alpha:1].CGColor,
                       (id)[UIColor colorWithRed:gradientShade green:gradientShade blue:gradientShade alpha:.9].CGColor,
                       (id)[UIColor colorWithRed:gradientShade green:gradientShade blue:gradientShade alpha:.8].CGColor,
                       (id)[UIColor colorWithRed:gradientShade green:gradientShade blue:gradientShade alpha:.6].CGColor,
                       (id)[UIColor colorWithRed:gradientShade green:gradientShade blue:gradientShade alpha:7].CGColor,
                       nil];
    [self.layer addSublayer:gradient];
    [self addSubview:gradientS];
    [self addSubview:_label];
  }
  return self;
}

- (void)dealloc
{
  [_label release];
  [_boundaries release];
  [_menu release];
  [super dealloc];
}


- (void)scrollViewDidScroll:(UIScrollView *)scrollView {
  NSInteger index = -1;
  for (NSInteger i = 0; i < [self.boundaries count]; i++) {
    NSNumber* number = [self.boundaries objectAtIndex:i];
    if ([number floatValue] < scrollView.contentOffset.y) {
      index = i;
    }
  }
  if (index == [self.boundaries count]) {
    index = [self.boundaries count] - 1;
  }
  if (index != -1) {
    assert(index < [self.boundaries count]);
    id<STSubmenu> submenu = [self.menu.menus objectAtIndex:index];
    if (submenu.title) {
      _label.text = submenu.title;
    }
  }
}


@end

@implementation STMenuPopUpHeaderGradient

- (id)initWithFrame:(CGRect)frame {
  self = [super initWithFrame:frame];
  if (self) {
    self.backgroundColor = [UIColor clearColor];
  }
  return self;
}

- (void)drawRect:(CGRect)rect {
  [super drawRect:rect];
  
  CGContextRef c = UIGraphicsGetCurrentContext();
  
  
  CGFloat color[4] = {0.8f, 0.8f, 0.8f, 1};
  CGFloat color2[4] = {0.8f, 0.8f, 0.8f, .8f};
  CGContextSetStrokeColor(c, color2);
  CGContextBeginPath(c);
  CGContextMoveToPoint(c, 0, self.frame.size.height);
  CGContextSetLineWidth(c, 2);
  CGContextAddLineToPoint(c, self.frame.size.width, self.frame.size.height);
  CGContextStrokePath(c);
  
  CGContextSetStrokeColor(c, color);
  CGContextBeginPath(c);
  CGContextMoveToPoint(c, 0, 0.0f);
  CGContextSetLineWidth(c, 2);
  CGContextAddLineToPoint(c, self.frame.size.width, 0);
  CGContextStrokePath(c);
}

@end
