//
//  PairedLabel.h
//  Stamped
//
//  Created by Jake Zien on 9/9/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface PairedLabel : UIViewController {
  @protected
    CGFloat nameWidth;
    CGFloat numberWidth;
}

@property (nonatomic, retain) IBOutlet UILabel* nameLabel;
@property (nonatomic, retain) IBOutlet UILabel* valueLabel;
@property (nonatomic, assign) CGFloat nameWidth;
@property (nonatomic, assign) CGFloat numberWidth;

- (NSUInteger)lineCountOfLabel:(UILabel*)label;

@end
