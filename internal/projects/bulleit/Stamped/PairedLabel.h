//
//  PairedLabel.h
//  Stamped
//
//  Created by Jake Zien on 9/9/11.
//  Copyright 2011 RISD. All rights reserved.
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

@end
