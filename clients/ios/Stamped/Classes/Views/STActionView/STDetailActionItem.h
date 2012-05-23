//
//  STDetailActionItem.h
//  Stamped
//
//  Created by Devin Doty on 5/16/12.
//
//

#import <UIKit/UIKit.h>

@protocol STDetailActionItem <NSObject>

/*
 * name of the image for the item
 */
@property(nonatomic,copy) NSString *imageName;


/*
 * name of the highlighted state image for the item
 */
@property(nonatomic,copy) NSString *imageNameHighlighted;

/*
 * name of the selected state image for the item
 */
@property (nonatomic,copy) NSString *imageNameSelected;

/*
 * button action target
 */
@property(nonatomic,assign) id target;

/*
 * button selector
 */
@property(nonatomic,assign) SEL selector;

@end