//
//  STMultipleChoiceButton.m
//  Stamped
//
//  Created by Landon Judkins on 4/9/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STMultipleChoiceButton.h"
#import "Util.h"

@interface STMultipleChoiceButton ()

- (void)clicked:(id)myself;

@property (nonatomic, readonly, copy) NSArray* choices;
@property (nonatomic, readonly, copy) NSString* title;
@property (nonatomic, readonly, copy) NSString* message;
@property (nonatomic, readwrite, assign) id target;
@property (nonatomic, readwrite, assign) SEL selector;

@end

@implementation STMultipleChoiceButton

@synthesize choices = _choices;
@synthesize title = _title;
@synthesize message = _message;
@synthesize selectedChoice = _selectedChoice;
@synthesize target = _target;
@synthesize selector = _selector;

- (id)initWithTitle:(NSString*)title message:(NSString*)message choices:(NSArray*)choices andFrame:(CGRect)frame {
  self = [super initWithFrame:frame];
  if (self) {
    _choices = [choices copy];
    NSAssert([_choices count] > 0,@"choices must be non-empty");
    _selectedChoice = [[_choices objectAtIndex:0] copy];
    _title = [title copy];
    _message = [message copy];
    [self setTitle:_selectedChoice forState:UIControlStateNormal];
    [self setBackgroundImage:[UIImage imageNamed:@"green_button_bg"] forState:UIControlStateNormal];
    [self addTarget:self action:@selector(clicked:) forControlEvents:UIControlEventTouchUpInside];
  }
  return self;
}

- (void)dealloc
{
  [_choices release];
  [_selectedChoice release];
  [_title release];
  [_message release];
  [super dealloc];
}

- (void)clicked:(id)myself {
  [Util menuWithTitle:self.title message:self.message choices:self.choices andBlock:^(NSString *string) {
    
    if (string) {
      [_selectedChoice release];
      _selectedChoice = [string copy];
      [self setTitle:_selectedChoice forState:UIControlStateNormal];
      if (self.target && self.selector) {
        [self.target performSelector:self.selector withObject:string];
      }
    }
    
  }];
}

- (void)setTarget:(id)target withSelector:(SEL)selector {
  self.selector = selector;
  self.target = target;
}

@end
